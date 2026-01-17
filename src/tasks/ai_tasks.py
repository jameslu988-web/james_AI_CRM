"""
AI相关异步任务
包括：邮件AI分析、AI回复生成等
"""

from src.celery_config import celery_app
from src.crm.database import get_session, EmailHistory
from src.ai.email_analyzer import get_analyzer
import traceback
import asyncio
import json


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
