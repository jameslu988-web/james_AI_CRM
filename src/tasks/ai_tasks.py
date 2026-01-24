"""
AI相关异步任务
包括：邮件AI分析、AI回复生成等
"""

from src.celery_config import celery_app
from src.crm.database import get_session, EmailHistory, AutoReplyRule, ApprovalTask
from src.ai.email_analyzer import get_analyzer
import traceback
import asyncio
import json
from datetime import datetime, timedelta


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def analyze_email_task(self, email_id: int):
    """
    异步AI分析邮件任务
    
    参数:
        email_id: 邮件ID
    """
    db = get_session()
    
    try:
        email = db.query(EmailHistory).filter(EmailHistory.id == email_id).first()
        
        if not email:
            return {"error": "邮件不存在", "email_id": email_id}
        
        print(f"🤖 开始AI分析邮件: {email.subject}")
        
        # 获取 AI 分析器
        analyzer = get_analyzer()
        
        # 异步调用 AI 分析（在同步函数中运行异步代码）
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                analyzer.analyze_email(
                    subject=email.subject or "",
                    body=email.body or "",
                    from_email=email.from_email
                )
            )
        finally:
            loop.close()
        
        if result['success']:
            analysis = result['analysis']
            
            # 更新邮件的所有AI字段（完整版）
            # 基础分析
            email.ai_sentiment = analysis.get('sentiment', 'neutral')
            email.ai_category = analysis.get('category', 'spam')  # 默认为spam（垃圾营销）
            email.urgency_level = analysis.get('urgency_level', 'medium')
            email.purchase_intent = analysis.get('purchase_intent', 'low')
            email.ai_summary = analysis.get('summary', '')
            
            # 业务阶段
            email.business_stage = analysis.get('business_stage')
            email.secondary_category = analysis.get('secondary_category')
            
            # 客户意图
            email.purchase_intent_score = analysis.get('purchase_intent_score')
            email.budget_level = analysis.get('budget_level')
            email.decision_authority = analysis.get('decision_authority')
            email.competition_status = analysis.get('competition_status')
            email.customer_business_type = analysis.get('customer_business_type')
            
            # 情感态度
            email.tone = analysis.get('tone')
            email.satisfaction_level = analysis.get('satisfaction_level')
            
            # 紧急度
            email.response_deadline = analysis.get('response_deadline')
            email.business_impact = analysis.get('business_impact')
            
            # 客户画像
            email.customer_type = analysis.get('customer_type')
            email.customer_grade_suggestion = analysis.get('customer_grade_suggestion')
            email.professionalism = analysis.get('professionalism')
            email.communication_style = analysis.get('communication_style')
            
            # 行动建议
            email.next_action = analysis.get('next_action')
            email.response_template_suggestion = analysis.get('response_template_suggestion')
            email.requires_human_review = analysis.get('requires_human_review')
            email.human_review_reason = analysis.get('human_review_reason')
            
            # 风险机会
            email.risk_level = analysis.get('risk_level')
            if analysis.get('risk_factors'):
                email.risk_factors = json.dumps(analysis['risk_factors'], ensure_ascii=False)
            email.opportunity_score = analysis.get('opportunity_score')
            email.conversion_probability = analysis.get('conversion_probability')
            email.estimated_order_value = analysis.get('estimated_order_value')
            
            # 内容分析（JSON格式）
            if analysis.get('mentioned_products'):
                email.mentioned_products = json.dumps(analysis['mentioned_products'], ensure_ascii=False)
            if analysis.get('questions_asked'):
                email.questions_asked = json.dumps(analysis['questions_asked'], ensure_ascii=False)
            if analysis.get('concerns'):
                email.concerns = json.dumps(analysis['concerns'], ensure_ascii=False)
            email.mentioned_quantities = analysis.get('mentioned_quantities')
            email.mentioned_prices = analysis.get('mentioned_prices')
            email.mentioned_timeline = analysis.get('mentioned_timeline')
            
            # 存储建议标签
            if analysis.get('suggested_tags'):
                email.tags = json.dumps(analysis['suggested_tags'], ensure_ascii=False)
            
            # 跟进日期
            if analysis.get('follow_up_date'):
                try:
                    # 假设返回的是天数
                    days = int(analysis['follow_up_date'])
                    from datetime import timedelta
                    email.follow_up_date = email.sent_at + timedelta(days=days)
                except:
                    pass
            
            db.commit()
            
            print(f"✅ AI分析完成: {email.subject}")
            print(f"   - 业务阶段: {email.business_stage}")
            print(f"   - 情感: {email.ai_sentiment}")
            print(f"   - 类别: {email.ai_category}")
            print(f"   - 紧急度: {email.urgency_level}")
            print(f"   - 购买意向: {email.purchase_intent} ({email.purchase_intent_score}分)")
            print(f"   - 客户分级: {email.customer_grade_suggestion}")
            
            # 🔥 新增：检查是否匹配自动回复规则
            if email.ai_category:
                print(f"\n🔍 检查自动回复规则: 邮件类型={email.ai_category}")
                trigger_auto_reply_if_matched(email.id, email.ai_category, db)
            
            return {
                "success": True,
                "email_id": email_id,
                "analysis": analysis,
                "message": "AI分析完成"
            }
        else:
            print(f"⚠️ AI分析返回失败: {result.get('error')}")
            return {
                "success": False,
                "email_id": email_id,
                "error": result.get('error'),
                "message": "AI分析失败"
            }
        
    except Exception as e:
        print(f"❌ AI分析任务失败: {str(e)}")
        traceback.print_exc()
        raise self.retry(exc=e)
        
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def generate_reply_task(self, email_id: int, tone: str = "professional"):
    """
    异步AI生成回复任务
    
    参数:
        email_id: 邮件ID
        tone: 回复语气 (professional/friendly/formal)
    """
    db = get_session()
    
    try:
        email = db.query(EmailHistory).filter(EmailHistory.id == email_id).first()
        
        if not email:
            return {"error": "邮件不存在", "email_id": email_id}
        
        print(f"🤖 开始AI生成回复: {email.subject}")
        
        # 获取 AI 分析器
        analyzer = get_analyzer()
        
        # 异步调用 AI 生成回复
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 准备上下文信息
            context = {}
            if email.customer:
                context['customer_name'] = email.customer.contact_name
                context['company_name'] = email.customer.company_name
            
            result = loop.run_until_complete(
                analyzer.generate_reply(
                    subject=email.subject or "",
                    body=email.body or "",
                    context=context,
                    tone=tone
                )
            )
        finally:
            loop.close()
        
        if result['success']:
            print(f"✅ AI回复生成完成: {email.subject}")
            
            return {
                "success": True,
                "email_id": email_id,
                "reply": result['reply'],
                "message": "AI回复生成完成"
            }
        else:
            print(f"⚠️ AI回复生成失败: {result.get('error')}")
            return {
                "success": False,
                "email_id": email_id,
                "error": result.get('error'),
                "message": "AI回复生成失败"
            }
        
    except Exception as e:
        print(f"❌ AI回复生成失败: {str(e)}")
        traceback.print_exc()
        raise self.retry(exc=e)
        
    finally:
        db.close()


def trigger_auto_reply_if_matched(email_id: int, email_category: str, db):
    """
    检查是否匹配自动回复规则，如果匹配则触发自动回复
    
    参数:
        email_id: 邮件ID
        email_category: 邮件类型 (inquiry/quotation/sample等)
        db: 数据库会话
    """
    try:
        # 查询匹配的规则（启用的且需要自动生成回复的）
        rules = db.query(AutoReplyRule).filter(
            AutoReplyRule.email_category == email_category,
            AutoReplyRule.is_enabled == True,
            AutoReplyRule.auto_generate_reply == True
        ).order_by(AutoReplyRule.priority.desc()).all()
        
        if not rules:
            print(f"❌ 未找到匹配的自动回复规则: {email_category}")
            return
        
        # 使用优先级最高的规则
        rule = rules[0]
        print(f"✅ 匹配到规则: {rule.rule_name} (ID={rule.id})")
        
        # 更新规则统计
        rule.triggered_count = (rule.triggered_count or 0) + 1
        db.commit()
        
        # 异步触发AI生成回复任务
        print(f"🤖 触发AI生成回复任务...")
        generate_auto_reply_task.delay(email_id, rule.id)
        
    except Exception as e:
        print(f"⚠️ 检查自动回复规则失败: {str(e)}")
        traceback.print_exc()


@celery_app.task(bind=True, max_retries=3)
def generate_auto_reply_task(self, email_id: int, rule_id: int):
    """
    异步AI生成自动回复并创建审核任务
    
    参数:
        email_id: 原始邮件ID
        rule_id: 触发的规则ID
    """
    db = get_session()
    
    try:
        # 获取邮件和规则
        email = db.query(EmailHistory).filter(EmailHistory.id == email_id).first()
        rule = db.query(AutoReplyRule).filter(AutoReplyRule.id == rule_id).first()
        
        if not email or not rule:
            return {"error": "邮件或规则不存在"}
        
        print(f"\n🤖 开始生成自动回复: {email.subject}")
        print(f"   触发规则: {rule.rule_name}")
        print(f"   邮件类型: {email.ai_category}")
        
        # 获取AI分析器
        analyzer = get_analyzer()
        
        # 准备上下文信息
        context = {
            'email_category': email.ai_category,
            'sentiment': email.ai_sentiment,
            'purchase_intent': email.purchase_intent,
            'urgency_level': email.urgency_level,
        }
        
        if email.customer:
            context['customer_name'] = email.customer.contact_name
            context['company_name'] = email.customer.company_name
        
        # 🔥 获取默认的专业外贸回复模板
        from src.crm.database import PromptTemplate
        
        default_template = db.query(PromptTemplate).filter_by(
            is_default=True,
            template_type='reply',
            is_active=True
        ).first()
        
        # 构建自定义提示词（如果有默认模板）
        custom_prompt = None
        if default_template:
            custom_prompt = {
                'system_prompt': default_template.system_prompt,
                'user_prompt_template': default_template.user_prompt_template
            }
            print(f"✅ 使用专业外贸回复模板: {default_template.name}")
        else:
            print(f"⚠️ 未找到默认模板，使用硬编码默认提示词")
        
        # 调用AI生成回复
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                analyzer.generate_reply(
                    subject=email.subject or "",
                    body=email.body or "",
                    context=context,
                    tone="professional",
                    custom_prompt=custom_prompt  # 🔥 传入自定义提示词
                )
            )
        finally:
            loop.close()
        
        if not result.get('success'):
            print(f"❌ AI生成回复失败: {result.get('error')}")
            return {"success": False, "error": result.get('error')}
        
        reply = result['reply']
        print(f"✅ AI回复生成成功")
        
        # 🔥 修复：reply 是字符串，不是字典
        draft_subject = f"Re: {email.subject}"
        draft_body = reply  # HTML内容
        draft_html = reply  # HTML内容
        print(f"   主题: {draft_subject}")
        print(f"   正文长度: {len(draft_body)} 字符")
        
        # 创建审核任务
        approval_task = ApprovalTask(
            email_id=email.id,
            rule_id=rule.id,
            draft_subject=draft_subject,
            draft_body=draft_body,
            draft_html=draft_html,
            status='pending',
            approval_method=rule.approval_method,
            auto_send_on_approval=True,
            timeout_at=datetime.utcnow() + timedelta(hours=rule.approval_timeout_hours or 24),
            ai_analysis_summary=json.dumps({
                'category': email.ai_category,
                'sentiment': email.ai_sentiment,
                'purchase_intent': email.purchase_intent,
                'urgency_level': email.urgency_level,
                'summary': email.ai_summary
            }, ensure_ascii=False)
        )
        
        db.add(approval_task)
        db.commit()
        
        print(f"✅ 审核任务已创建: ID={approval_task.id}")
        print(f"   审核方式: {approval_task.approval_method}")
        print(f"   超时时间: {approval_task.timeout_at}")
        
        # 🔥 如果审核方式是企业微信，发送通知
        if approval_task.approval_method == 'wechat':
            try:
                from src.utils.wecom_notification import get_wecom_notification
                
                wecom = get_wecom_notification()
                wecom.send_approval_notification(
                    task_id=approval_task.id,
                    email_subject=email.subject or '（无主题）',
                    email_from=email.from_email or '（未知）',
                    email_category=email.ai_category or 'inquiry',
                    draft_subject=draft_subject,
                    urgency_level=email.urgency_level or 'medium',
                    use_webhook=True
                )
                print(f"✅ 已发送企业微信审核通知")
            except Exception as e:
                print(f"❌ 发送企业微信通知失败: {str(e)}")
        
        return {
            "success": True,
            "email_id": email_id,
            "rule_id": rule_id,
            "approval_task_id": approval_task.id,
            "message": "自动回复已生成，等待审核"
        }
        
    except Exception as e:
        print(f"❌ 生成自动回复失败: {str(e)}")
        traceback.print_exc()
        raise self.retry(exc=e)
        
    finally:
        db.close()
