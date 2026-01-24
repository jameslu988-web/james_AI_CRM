"""
自动回复规则和审核任务 API
提供规则管理和审核功能的接口
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from src.crm.database import get_session, AutoReplyRule, ApprovalTask, EmailHistory, EmailAccount
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import json

router = APIRouter()

# ==================== Pydantic Schemas ====================

class AutoReplyRuleBase(BaseModel):
    rule_name: str
    email_category: str
    is_enabled: bool = True
    auto_generate_reply: bool = True
    require_approval: bool = True
    approval_method: str = 'system'
    approval_timeout_hours: int = 24
    priority: int = 0
    conditions: Optional[str] = None

class AutoReplyRuleCreate(AutoReplyRuleBase):
    pass

class AutoReplyRuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    email_category: Optional[str] = None
    is_enabled: Optional[bool] = None
    auto_generate_reply: Optional[bool] = None
    require_approval: Optional[bool] = None
    approval_method: Optional[str] = None
    approval_timeout_hours: Optional[int] = None
    priority: Optional[int] = None
    conditions: Optional[str] = None

class AutoReplyRuleOut(BaseModel):
    id: int
    rule_name: str
    email_category: str
    is_enabled: bool = True
    auto_generate_reply: bool = True
    require_approval: bool = True
    approval_method: Optional[str] = 'system'
    approval_timeout_hours: Optional[int] = 24
    priority: int = 0
    conditions: Optional[str] = None
    triggered_count: Optional[int] = 0
    approved_count: Optional[int] = 0
    rejected_count: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ApprovalTaskBase(BaseModel):
    email_id: int
    rule_id: Optional[int] = None
    draft_subject: str
    draft_body: str
    draft_html: Optional[str] = None
    status: str = 'pending'
    approval_method: str = 'system'
    auto_send_on_approval: bool = True
    ai_analysis_summary: Optional[str] = None

class ApprovalTaskCreate(ApprovalTaskBase):
    pass

class ApprovalTaskUpdate(BaseModel):
    status: Optional[str] = None
    approved_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    draft_subject: Optional[str] = None
    draft_body: Optional[str] = None
    draft_html: Optional[str] = None

class ApprovalTaskOut(ApprovalTaskBase):
    id: int
    notification_sent_at: Optional[datetime] = None
    notification_status: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    revision_count: int
    revision_history: Optional[str] = None
    sent_at: Optional[datetime] = None
    sent_email_id: Optional[int] = None
    timeout_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== 自动回复规则 API ====================

@router.get("/auto_reply_rules")
def get_auto_reply_rules(
    _start: int = 0,
    _end: int = 25,
    _sort: str = "priority",
    _order: str = "DESC",
    db: Session = Depends(get_session)
):
    """获取自动回复规则列表（React Admin兼容）"""
    try:
        query = db.query(AutoReplyRule)
        
        # 排序
        sort_column = getattr(AutoReplyRule, _sort, AutoReplyRule.id)
        if _order == "DESC":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # 总数
        total = query.count()
        
        # 分页
        items = query.offset(_start).limit(_end - _start).all()
        
        # 转换为字典
        result = []
        for item in items:
            item_dict = {
                "id": item.id,
                "rule_name": item.rule_name,
                "email_category": item.email_category,
                "is_enabled": item.is_enabled,
                "auto_generate_reply": item.auto_generate_reply,
                "require_approval": item.require_approval,
                "approval_method": item.approval_method,
                "approval_timeout_hours": item.approval_timeout_hours,
                "priority": item.priority,
                "conditions": item.conditions,
                "triggered_count": item.triggered_count,
                "approved_count": item.approved_count,
                "rejected_count": item.rejected_count,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            }
            result.append(item_dict)
        
        # 返回响应（包含Content-Range）
        return Response(
            content=json.dumps(result, ensure_ascii=False),
            media_type="application/json",
            headers={
                "Content-Range": f"items {_start}-{min(_end, total)}/{total}",
                "Access-Control-Expose-Headers": "Content-Range"
            }
        )
    finally:
        db.close()


@router.get("/auto_reply_rules/{id}", response_model=AutoReplyRuleOut)
def get_auto_reply_rule(id: int, db: Session = Depends(get_session)):
    """获取单个规则"""
    try:
        rule = db.query(AutoReplyRule).filter(AutoReplyRule.id == id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="规则不存在")
        return rule
    finally:
        db.close()


@router.post("/auto_reply_rules", response_model=AutoReplyRuleOut)
def create_auto_reply_rule(data: AutoReplyRuleCreate, db: Session = Depends(get_session)):
    """创建自动回复规则"""
    try:
        rule = AutoReplyRule(**data.dict())
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule
    finally:
        db.close()


@router.put("/auto_reply_rules/{id}", response_model=AutoReplyRuleOut)
def update_auto_reply_rule(id: int, data: AutoReplyRuleUpdate, db: Session = Depends(get_session)):
    """更新规则"""
    try:
        rule = db.query(AutoReplyRule).filter(AutoReplyRule.id == id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="规则不存在")
        
        for key, value in data.dict(exclude_unset=True).items():
            setattr(rule, key, value)
        
        rule.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(rule)
        return rule
    finally:
        db.close()


@router.delete("/auto_reply_rules/{id}")
def delete_auto_reply_rule(id: int, db: Session = Depends(get_session)):
    """删除规则"""
    try:
        rule = db.query(AutoReplyRule).filter(AutoReplyRule.id == id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="规则不存在")
        
        db.delete(rule)
        db.commit()
        return {"success": True}
    finally:
        db.close()


# ==================== 审核任务 API ====================

@router.get("/approval_tasks")
def get_approval_tasks(
    _start: int = 0,
    _end: int = 25,
    _sort: str = "created_at",
    _order: str = "DESC",
    status: Optional[str] = None,
    db: Session = Depends(get_session)
):
    """获取审核任务列表（React Admin兼容）"""
    try:
        query = db.query(ApprovalTask)
        
        # 筛选状态
        if status:
            query = query.filter(ApprovalTask.status == status)
        
        # 排序
        sort_column = getattr(ApprovalTask, _sort, ApprovalTask.created_at)
        if _order == "DESC":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # 总数
        total = query.count()
        
        # 分页
        items = query.offset(_start).limit(_end - _start).all()
        
        # 转换为字典（包含关联的邮件信息）
        result = []
        for item in items:
            # 获取关联的原始邮件
            email = db.query(EmailHistory).filter(EmailHistory.id == item.email_id).first()
            
            item_dict = {
                "id": item.id,
                "email_id": item.email_id,
                "rule_id": item.rule_id,
                "draft_subject": item.draft_subject,
                "draft_body": item.draft_body,
                "draft_html": item.draft_html,
                "status": item.status,
                "approval_method": item.approval_method,
                "notification_sent_at": item.notification_sent_at.isoformat() if item.notification_sent_at else None,
                "notification_status": item.notification_status,
                "approved_by": item.approved_by,
                "approved_at": item.approved_at.isoformat() if item.approved_at else None,
                "rejection_reason": item.rejection_reason,
                "revision_count": item.revision_count,
                "revision_history": item.revision_history,
                "auto_send_on_approval": item.auto_send_on_approval,
                "sent_at": item.sent_at.isoformat() if item.sent_at else None,
                "sent_email_id": item.sent_email_id,
                "timeout_at": item.timeout_at.isoformat() if item.timeout_at else None,
                "ai_analysis_summary": item.ai_analysis_summary,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
                # 关联邮件信息
                "original_email": {
                    "from_name": email.from_name if email else None,
                    "from_email": email.from_email if email else None,
                    "subject": email.subject if email else None,
                    "body": email.body if email else None,
                    "sent_at": email.sent_at.isoformat() if email and email.sent_at else None,
                    "ai_category": email.ai_category if email else None,
                } if email else None
            }
            result.append(item_dict)
        
        # 返回响应
        return Response(
            content=json.dumps(result, ensure_ascii=False),
            media_type="application/json",
            headers={
                "Content-Range": f"items {_start}-{min(_end, total)}/{total}",
                "Access-Control-Expose-Headers": "Content-Range"
            }
        )
    finally:
        db.close()


@router.get("/approval_tasks/{id}")
def get_approval_task(id: int, db: Session = Depends(get_session)):
    """获取单个审核任务（包含原始邮件信息）"""
    try:
        task = db.query(ApprovalTask).filter(ApprovalTask.id == id).first()
        if not task:
            raise HTTPException(status_code=404, detail="审核任务不存在")
        
        # 获取关联的原始邮件
        email = db.query(EmailHistory).filter(EmailHistory.id == task.email_id).first()
        
        # 构建响应
        result = {
            "id": task.id,
            "email_id": task.email_id,
            "rule_id": task.rule_id,
            "draft_subject": task.draft_subject,
            "draft_body": task.draft_body,
            "draft_html": task.draft_html,
            "status": task.status,
            "approval_method": task.approval_method,
            "notification_sent_at": task.notification_sent_at.isoformat() if task.notification_sent_at else None,
            "notification_status": task.notification_status,
            "approved_by": task.approved_by,
            "approved_at": task.approved_at.isoformat() if task.approved_at else None,
            "rejection_reason": task.rejection_reason,
            "revision_count": task.revision_count,
            "revision_history": task.revision_history,
            "auto_send_on_approval": task.auto_send_on_approval,
            "sent_at": task.sent_at.isoformat() if task.sent_at else None,
            "sent_email_id": task.sent_email_id,
            "timeout_at": task.timeout_at.isoformat() if task.timeout_at else None,
            "ai_analysis_summary": task.ai_analysis_summary,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            # 关联邮件信息（包含正文）
            "original_email": {
                "from_name": email.from_name if email else None,
                "from_email": email.from_email if email else None,
                "subject": email.subject if email else None,
                "body": email.body if email else None,
                "html_body": email.html_body if email else None,
                "sent_at": email.sent_at.isoformat() if email and email.sent_at else None,
                "ai_category": email.ai_category if email else None,
                "ai_sentiment": email.ai_sentiment if email else None,
                "purchase_intent": email.purchase_intent if email else None,
                "urgency_level": email.urgency_level if email else None,
            } if email else None
        }
        
        return Response(
            content=json.dumps(result, ensure_ascii=False),
            media_type="application/json"
        )
    finally:
        db.close()


@router.post("/approval_tasks", response_model=ApprovalTaskOut)
def create_approval_task(data: ApprovalTaskCreate, db: Session = Depends(get_session)):
    """创建审核任务"""
    try:
        # 设置超时时间
        rule = None
        if data.rule_id:
            rule = db.query(AutoReplyRule).filter(AutoReplyRule.id == data.rule_id).first()
        
        timeout_hours = rule.approval_timeout_hours if rule else 24
        timeout_at = datetime.utcnow() + timedelta(hours=timeout_hours)
        
        task = ApprovalTask(
            **data.dict(),
            timeout_at=timeout_at
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # 🔥 如果审核方式是企业微信，发送通知
        if task.approval_method == 'wechat':
            try:
                from src.utils.wecom_notification import get_wecom_notification
                
                # 获取原始邮件信息
                email = db.query(EmailHistory).filter(EmailHistory.id == task.email_id).first()
                
                if email:
                    wecom = get_wecom_notification()
                    wecom.send_approval_notification(
                        task_id=task.id,
                        email_subject=email.subject or '（无主题）',
                        email_from=email.from_email or '（未知）',
                        email_category=email.ai_category or 'inquiry',
                        draft_subject=task.draft_subject,
                        urgency_level=email.urgency_level or 'medium',
                        use_webhook=True  # 默认使用群机器人
                    )
                    print(f"✅ 已发送企业微信审核通知: 任务ID={task.id}")
                else:
                    print(f"⚠️ 找不到原始邮件: email_id={task.email_id}")
                    
            except Exception as e:
                print(f"❌ 发送企业微信通知失败: {str(e)}")
                import traceback
                traceback.print_exc()
        
        return task
    finally:
        db.close()


@router.put("/approval_tasks/{id}/approve")
def approve_task(id: int, approved_by: str, db: Session = Depends(get_session)):
    """通过审核（并自动发送邮件）"""
    try:
        task = db.query(ApprovalTask).filter(ApprovalTask.id == id).first()
        if not task:
            raise HTTPException(status_code=404, detail="审核任务不存在")
        
        # 更新审核状态
        task.status = 'approved'
        task.approved_by = approved_by
        task.approved_at = datetime.utcnow()
        
        # 更新规则统计
        if task.rule_id:
            rule = db.query(AutoReplyRule).filter(AutoReplyRule.id == task.rule_id).first()
            if rule:
                rule.approved_count += 1
        
        db.commit()
        
        # 如果设置了自动发送，则发送邮件
        if task.auto_send_on_approval:
            try:
                # 获取原始邮件
                email = db.query(EmailHistory).filter(EmailHistory.id == task.email_id).first()
                
                if not email:
                    return {"success": True, "message": "审核通过，但找不到原始邮件"}
                
                # 查找发件人账户（假设使用第一个启用的账户）
                account = db.query(EmailAccount).filter(
                    EmailAccount.is_active == True
                ).first()
                
                if not account or not account.smtp_host or not account.smtp_password:
                    return {
                        "success": True, 
                        "message": "审核通过，但未配置SMTP，无法自动发送",
                        "warning": "NO_SMTP_CONFIG"
                    }
                
                # 配置SMTP
                from src.email_system.sender import EmailSender
                smtp_config = {
                    'host': account.smtp_host,
                    'port': account.smtp_port,
                    'username': account.smtp_username or account.email_address,
                    'password': account.smtp_password,
                    'use_ssl': account.smtp_port == 465
                }
                
                sender = EmailSender(smtp_config=smtp_config)
                
                # 发送邮件
                result = sender.send_email(
                    to_email=email.from_email,  # 回复给原始发件人
                    subject=task.draft_subject,
                    body=task.draft_body,
                    from_email=account.email_address,
                    from_name=account.account_name,
                    html_body=task.draft_html
                )
                
                if result['success']:
                    # 记录发送成功
                    task.sent_at = datetime.utcnow()
                    
                    # 🔥 关键修复：创建发送记录时必须包含customer_id，确保出站邮件不会出现在收件箱
                    # 🔥 调试：打印customer_id信息
                    print(f"🔍 调试信息:")
                    print(f"   原始邮件ID: {email.id}")
                    print(f"   原始邮件customer_id: {email.customer_id}")
                    print(f"   原始邮件from_email: {email.from_email}")
                    
                    sent_email = EmailHistory(
                        customer_id=email.customer_id,  # 从原始邮件继承customer_id
                        from_email=account.email_address,
                        from_name=account.account_name,
                        to_email=email.from_email,
                        to_name=email.from_name,
                        subject=task.draft_subject,
                        body=task.draft_body,
                        html_body=task.draft_html,
                        direction='outbound',
                        status='sent',
                        delivery_status='delivered',
                        sent_at=datetime.utcnow()
                    )
                    
                    print(f"   创建的sent_email.customer_id: {sent_email.customer_id}")
                    
                    db.add(sent_email)
                    db.commit()
                    db.refresh(sent_email)
                    
                    print(f"   保存后sent_email.customer_id: {sent_email.customer_id}")
                    print(f"   保存后sent_email.id: {sent_email.id}")
                    
                    task.sent_email_id = sent_email.id
                    
                    # 更新原始邮件的replied状态
                    email.replied = True
                    
                    # 更新账户统计
                    account.total_sent = (account.total_sent or 0) + 1
                    
                    db.commit()
                    
                    print(f"✅ 审核通过并自动发送成功: {email.from_email}")
                    
                    # 🔥 发送企业微信通知
                    if task.approval_method == 'wechat':
                        try:
                            from src.utils.wecom_notification import get_wecom_notification
                            wecom = get_wecom_notification()
                            wecom.send_approval_result_notification(
                                task_id=task.id,
                                status='approved',
                                approved_by=approved_by,
                                email_subject=task.draft_subject,
                                use_webhook=True
                            )
                        except Exception as e:
                            print(f"❌ 发送企业微信通知失败: {str(e)}")
                    
                    return {
                        "success": True, 
                        "message": "审核通过，邮件已自动发送",
                        "sent_email_id": sent_email.id
                    }
                else:
                    print(f"⚠️ 审核通过，但发送失败: {result['message']}")
                    return {
                        "success": True, 
                        "message": f"审核通过，但发送失败: {result['message']}",
                        "warning": "SEND_FAILED"
                    }
                    
            except Exception as e:
                print(f"❌ 自动发送异常: {str(e)}")
                import traceback
                traceback.print_exc()
                return {
                    "success": True, 
                    "message": f"审核通过，但发送异常: {str(e)}",
                    "warning": "SEND_ERROR"
                }
        
        return {"success": True, "message": "审核通过"}
    finally:
        db.close()


@router.put("/approval_tasks/{id}/reject")
def reject_task(id: int, rejected_by: str, reason: Optional[str] = None, db: Session = Depends(get_session)):
    """拒绝审核"""
    try:
        task = db.query(ApprovalTask).filter(ApprovalTask.id == id).first()
        if not task:
            raise HTTPException(status_code=404, detail="审核任务不存在")
        
        task.status = 'rejected'
        task.approved_by = rejected_by
        task.approved_at = datetime.utcnow()
        task.rejection_reason = reason
        
        # 更新规则统计
        if task.rule_id:
            rule = db.query(AutoReplyRule).filter(AutoReplyRule.id == task.rule_id).first()
            if rule:
                rule.rejected_count += 1
        
        db.commit()
        
        # 🔥 发送企业微信通知
        if task.approval_method == 'wechat':
            try:
                from src.utils.wecom_notification import get_wecom_notification
                
                # 获取原始邮件
                email = db.query(EmailHistory).filter(EmailHistory.id == task.email_id).first()
                email_subject = email.subject if email else task.draft_subject
                
                wecom = get_wecom_notification()
                wecom.send_approval_result_notification(
                    task_id=task.id,
                    status='rejected',
                    approved_by=rejected_by,
                    email_subject=email_subject,
                    use_webhook=True
                )
                print(f"✅ 已发送企业微信拒绝通知: 任务ID={task.id}")
            except Exception as e:
                print(f"❌ 发送企业微信通知失败: {str(e)}")
        
        return {"success": True, "message": "已拒绝"}
    finally:
        db.close()


@router.put("/approval_tasks/{id}")
def update_approval_task(id: int, data: ApprovalTaskUpdate, db: Session = Depends(get_session)):
    """更新审核任务（用于修改内容）"""
    try:
        task = db.query(ApprovalTask).filter(ApprovalTask.id == id).first()
        if not task:
            raise HTTPException(status_code=404, detail="审核任务不存在")
        
        # 如果修改了内容，增加修改次数
        if data.draft_body or data.draft_html:
            task.revision_count += 1
            
            # 记录修改历史
            history = json.loads(task.revision_history) if task.revision_history else []
            history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "changes": data.dict(exclude_unset=True)
            })
            task.revision_history = json.dumps(history, ensure_ascii=False)
        
        for key, value in data.dict(exclude_unset=True).items():
            setattr(task, key, value)
        
        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        
        return task
    finally:
        db.close()


@router.post("/approval_tasks/{id}/regenerate")
async def regenerate_ai_reply(id: int, instruction: str = None, db: Session = Depends(get_session)):
    """AI重新生成回复"""
    try:
        task = db.query(ApprovalTask).filter(ApprovalTask.id == id).first()
        if not task:
            raise HTTPException(status_code=404, detail="审核任务不存在")
        
        # 获取原始邮件
        email = db.query(EmailHistory).filter(EmailHistory.id == task.email_id).first()
        if not email:
            raise HTTPException(status_code=404, detail="原始邮件不存在")
        
        # 导入AI分析器
        from src.ai.email_analyzer import EmailAIAnalyzer
        from openai import AsyncOpenAI
        import os
        
        # 如果有用户调整指令，使用专门的调整模式
        if instruction and instruction.strip():
            # 使用OpenAI直接调整现有内容
            client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            prompt = f"""你是一个专业的邮件编辑助手。用户对现有的邮件回复不满意，需要你根据用户的要求进行调整。

当前邮件回复内容：
主题：{task.draft_subject}
正文：
{task.draft_html or task.draft_body}

用户的调整要求：
{instruction}

请根据用户的要求，对上述邮件内容进行调整。要求：
1. **保持原邮件的整体结构和核心信息**
2. **只调整用户要求修改的部分**
3. **使用HTML格式**，使用<p>标签分段，使用<br>换行
4. **不要生成完整的HTML文档**（不要包含<!DOCTYPE>, <html>, <head>, <body>等标签）
5. **直接返回调整后的邮件正文HTML片段**
6. 保持专业、礼貌的语气
7. 如果原邮件是英文，调整后也应该是英文

请直接返回调整后的HTML邮件正文（从问候语开始）：
"""
            
            try:
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "你是一个专业的邮件编辑助手，擅长根据用户要求调整邮件内容。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                
                adjusted_content = response.choices[0].message.content.strip()
                
                # 清理可能的代码块标记
                import re
                adjusted_content = re.sub(r'^```html\s*', '', adjusted_content, flags=re.IGNORECASE)
                adjusted_content = re.sub(r'\s*```$', '', adjusted_content)
                adjusted_content = adjusted_content.strip()
                
                # 更新审核任务
                task.draft_html = adjusted_content
                task.draft_body = adjusted_content
                task.revision_count += 1
                task.updated_at = datetime.utcnow()
                
                # 记录修改历史
                history = json.loads(task.revision_history) if task.revision_history else []
                history.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "ai_adjust",
                    "instruction": instruction
                })
                task.revision_history = json.dumps(history, ensure_ascii=False)
                
                db.commit()
                db.refresh(task)
                
                print(f"✅ AI调整成功: 任务ID {task.id}, 指令: {instruction}")
                return {"success": True, "message": "AI调整成功"}
                
            except Exception as e:
                print(f"❌ AI调整失败: {str(e)}")
                raise HTTPException(status_code=500, detail=f"AI调整失败: {str(e)}")
        
        else:
            # 没有特殊指令，重新生成整封邮件
            analyzer = EmailAIAnalyzer()
            
            # 构建上下文
            context = {
                "customer_name": email.from_name,
                "sender_email": email.from_email
            }
            
            # 生成回复
            reply_result = await analyzer.generate_reply(
                subject=email.subject,
                body=email.body,
                context=context,
                tone="professional",
                use_knowledge_base=True
            )
            
            if reply_result.get('success'):
                # 解析AI返回的内容
                reply_content = reply_result.get('reply', '')
                
                # 提取主题和正文
                subject = f"Re: {email.subject}"
                
                # 更新审核任务
                task.draft_subject = subject
                task.draft_body = reply_content
                task.draft_html = reply_content
                task.revision_count += 1
                task.updated_at = datetime.utcnow()
                
                # 记录修改历史
                history = json.loads(task.revision_history) if task.revision_history else []
                history.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "ai_regenerate",
                    "instruction": "完全重新生成",
                    "knowledge_used": reply_result.get('knowledge_used', False)
                })
                task.revision_history = json.dumps(history, ensure_ascii=False)
                
                db.commit()
                db.refresh(task)
                
                print(f"✅ AI重新生成成功: 任务ID {task.id}")
                return {"success": True, "message": "AI重新生成成功"}
            else:
                error_msg = reply_result.get('error', 'AI生成失败')
                print(f"❌ AI生成失败: {error_msg}")
                raise HTTPException(status_code=500, detail=f"AI生成失败: {error_msg}")
            
    except Exception as e:
        print(f"❌ AI重新生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI重新生成失败: {str(e)}")
    finally:
        db.close()
