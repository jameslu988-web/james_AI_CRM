from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse  # 🔥 新增
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from datetime import datetime
import json
import logging
from pathlib import Path  # 🔥 新增

from src.crm.database import get_session, EmailHistory, EmailAccount
from ..schemas import EmailCreate, EmailUpdate, EmailOut
from src.email_system.sender import EmailSender
from ..exceptions import BusinessException, DatabaseException, ResourceNotFoundException

router = APIRouter()
logger = logging.getLogger(__name__)


def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@router.get("/email_history", response_model=List[EmailOut])
def list_emails(
    response: Response,
    filter: str = Query("{}"),
    range: str = Query("[0,19]"),
    sort: str = Query('["sent_at","DESC"]'),  # 默认按发送时间倒序
    # 🔥 支持直接查询参数
    _start: int = Query(None),
    _end: int = Query(None),
    _sort: str = Query(None),
    _order: str = Query(None),
    business_stage: str = Query(None),  # 直接接收 business_stage 参数
    direction: str = Query(None),
    status: str = Query(None),
    is_deleted: str = Query(None),
    db: Session = Depends(get_db),
):
    import json
    from fastapi import Response
    from sqlalchemy import case, desc, asc
    
    try:
        # 🔥 支持两种参数格式
        # 格式1：React Admin 默认格式（filter/range/sort 为 JSON 字符串）
        # 格式2：直接查询参数（_start/_end/_sort/_order + 直接筛选字段）
        
        # 解析分页参数
        if _start is not None and _end is not None:
            start, end = _start, _end
        else:
            try:
                r = json.loads(range)
                start, end = int(r[0]), int(r[1])
            except Exception:
                start, end = 0, 19
        
        # 解析排序参数
        if _sort and _order:
            sort_field, sort_order = _sort, _order.upper()
        else:
            try:
                s = json.loads(sort)
                sort_field, sort_order = s[0], s[1]
            except Exception:
                sort_field, sort_order = "sent_at", "DESC"
        
        # 解析筛选参数
        try:
            f = json.loads(filter)
        except Exception:
            f = {}
        
        # 🔥 合并直接查询参数和 filter JSON
        if business_stage:
            f['business_stage'] = business_stage
        if direction:
            f['direction'] = direction
        if status:
            f['status'] = status
        if is_deleted:
            f['is_deleted'] = is_deleted
        
        query = db.query(EmailHistory)
        search = f.get("search", "")
        direction_filter = f.get("direction", "")
        opened = f.get("opened", "")
        replied = f.get("replied", "")
        customer_id = f.get("customer_id", "")
        status_filter = f.get("status", "")  # 新增：状态筛选
        is_deleted_filter = f.get("is_deleted", "")  # 新增：是否已删除筛选
        business_stage_filter = f.get("business_stage", "")  # 🔥 新增：业务阶段筛选
        
        # 🔥 筛选参数日志
        logger.debug(f"邮件列表筛选", extra={"filter": f, "business_stage": business_stage_filter})
        
        # 默认只显示未删除的邮件（除非明确查询已删除）
        if is_deleted_filter:
            is_deleted_bool = is_deleted_filter.lower() == 'true'
            query = query.filter(EmailHistory.is_deleted == is_deleted_bool)
        else:
            # 默认不显示已删除的邮件
            query = query.filter(EmailHistory.is_deleted == False)
            
        # 🔥 核心修改：默认不显示草稿邮件（除非明确查询草稿）
        if status_filter:
            # 如果明确指定了status，则按指定的状态筛选
            query = query.filter(EmailHistory.status == status_filter)
        else:
            # 如果没有指定status，默认过滤掉草稿邮件
            query = query.filter(EmailHistory.status != 'draft')
            
        if search:
            like = f"%{search}%"
            query = query.filter((EmailHistory.subject.ilike(like)) | (EmailHistory.body.ilike(like)))
        if direction_filter:
            query = query.filter(EmailHistory.direction == direction_filter)
        if opened:
            # 将字符串转为布尔值
            opened_bool = opened.lower() == 'true'
            query = query.filter(EmailHistory.opened == opened_bool)
        if replied:
            replied_bool = replied.lower() == 'true'
            query = query.filter(EmailHistory.replied == replied_bool)
        if customer_id:
            query = query.filter(EmailHistory.customer_id == int(customer_id))
        # 🔥 业务阶段筛选
        if business_stage_filter:
            # 安全筛选：仅匹配非空值
            query = query.filter(EmailHistory.business_stage == business_stage_filter)

        # 🔥 置顶排序：置顶的邮件始终排在最前面
        # 使用 case 语句：is_starred=True 的记录排序值为0，否则为1
        pin_order = case(
            (EmailHistory.is_starred == True, 0),
            else_=1
        )
        query = query.order_by(pin_order)
            
        # 然后按用户指定的字段排序
        if sort_field and hasattr(EmailHistory, sort_field):
            if sort_order == "DESC":
                query = query.order_by(desc(getattr(EmailHistory, sort_field)))
            else:
                query = query.order_by(asc(getattr(EmailHistory, sort_field)))

        total = query.count()
        items = query.offset(start).limit(end - start + 1).all()

        response.headers["Content-Range"] = f"email_history {start}-{min(end, start + len(items) - 1)}/{total}"
        response.headers["Access-Control-Expose-Headers"] = "Content-Range"
        return items
        
    except Exception as e:
        import traceback
        logger.error(f"邮件列表API错误", extra={"error": str(e), "traceback": traceback.format_exc()})
        raise BusinessException(f"获取邮件列表失败: {str(e)}")


@router.get("/email_history/{email_id}", response_model=EmailOut)
def get_email(email_id: int, db: Session = Depends(get_db)):
    e = db.query(EmailHistory).filter(EmailHistory.id == email_id).first()
    if not e:
        logger.warning(f"邮件不存在", extra={"email_id": email_id})
        raise ResourceNotFoundException("邮件不存在", details={"email_id": email_id})
    return e


@router.post("/email_history", response_model=EmailOut)
def create_email(email_in: EmailCreate, db: Session = Depends(get_db)):
    """创建邮件记录：如果 status='draft' 则只保存不发送，否则发送邮件"""
    data = email_in.dict()
    
    # 获取状态，默认为 'sent'
    email_status = data.get('status', 'sent')
    
    # 如果是草稿，只保存不发送
    if email_status == 'draft':
        # 🔥 草稿不设置 sent_at（sent_at 表示实际发送时间）
        # created_at 和 updated_at 由数据库模型自动设置
        data['sent_at'] = None
        data['direction'] = 'outbound'  # 草稿默认为出站
        
        email = EmailHistory(**data)
        db.add(email)
        db.commit()
        db.refresh(email)
        
        logger.info(f"草稿已保存", extra={"email_id": email.id, "subject": email.subject})
        return email
    
    # 以下是发送邮件的逻辑
    if not data.get("sent_at"):
        data["sent_at"] = datetime.now()
    
    # 如果是出站邮件，尝试真实发送
    send_error = None
    if data.get('direction') == 'outbound' and data.get('from_email') and data.get('to_email'):
        try:
            # 查找发件人账户的SMTP配置
            account = db.query(EmailAccount).filter(
                EmailAccount.email_address == data['from_email'],
                EmailAccount.is_active == True
            ).first()
            
            if account and account.smtp_host and account.smtp_password:
                # 配置SMTP
                smtp_config = {
                    'host': account.smtp_host,
                    'port': account.smtp_port,
                    'username': account.smtp_username or account.email_address,
                    'password': account.smtp_password,
                    'use_ssl': account.smtp_port == 465
                }
                
                # 创建发送器
                sender = EmailSender(smtp_config=smtp_config)
                
                # 发送邮件
                result = sender.send_email(
                    to_email=data['to_email'],
                    subject=data.get('subject', '(无主题)'),
                    body=data.get('body', ''),
                    from_email=data['from_email'],
                    from_name=account.account_name,
                    cc_email=data.get('cc_email'),
                    bcc_email=data.get('bcc_email'),
                    html_body=data.get('html_body'),
                    priority=data.get('priority', 'normal'),
                    need_receipt=data.get('need_receipt', False)
                )
                
                if not result['success']:
                    send_error = result['message']
                    logger.warning(f"邮件发送失败", extra={"to_email": data['to_email'], "error": send_error})
                    # 🔥 设置投递状态为失败
                    data['delivery_status'] = 'failed'
                else:
                    logger.info(f"邮件已通过SMTP发送", extra={"to_email": data['to_email'], "subject": data.get('subject')})
                    # 🔥 SMTP发送成功，设置为 pending（等待投递确认）
                    data['delivery_status'] = 'pending'
                    # 更新账户发送统计
                    account.total_sent += 1
                    db.commit()
            else:
                send_error = f"未找到发件人账户的SMTP配置: {data['from_email']}"
                logger.warning(f"SMTP配置缺失", extra={"from_email": data['from_email']})
                # 🔥 没有SMTP配置，设置为 unknown
                data['delivery_status'] = 'unknown'
                
        except Exception as e:
            send_error = f"发送异常: {str(e)}"
            logger.error(f"邮件发送异常", extra={"error": str(e), "to_email": data.get('to_email')})
            # 🔥 发送异常，设置为 failed
            data['delivery_status'] = 'failed'
            data['bounce_reason'] = str(e)
    
    # 保存邮件记录到数据库
    email = EmailHistory(**data)
    
    # 如果发送失败，在备注中记录错误
    if send_error:
        email.internal_notes = f"[发送失败] {send_error}"
    
    db.add(email)
    db.commit()
    db.refresh(email)
    
    # 如果发送失败，抛出HTTP异常
    if send_error:
        raise HTTPException(status_code=500, detail=send_error)
    
    return email


@router.put("/email_history/{email_id}", response_model=EmailOut)
def update_email(email_id: int, email_upd: EmailUpdate, db: Session = Depends(get_db)):
    """更新邮件：支持从草稿发送（status: draft -> sent）"""
    e = db.query(EmailHistory).filter(EmailHistory.id == email_id).first()
    if not e:
        logger.warning(f"更新邮件失败: 邮件不存在", extra={"email_id": email_id})
        raise ResourceNotFoundException("邮件不存在", details={"email_id": email_id})
    
    update_data = email_upd.dict(exclude_unset=True)
    
    # 如果从草稿变为已发送，尝试发送邮件
    if e.status == 'draft' and update_data.get('status') == 'sent':
        logger.info(f"尝试从草稿发送邮件", extra={"email_id": email_id})
        
        # 查找发件人账户的SMTP配置
        if e.from_email and e.to_email:
            try:
                account = db.query(EmailAccount).filter(
                    EmailAccount.email_address == e.from_email,
                    EmailAccount.is_active == True
                ).first()
                
                if account and account.smtp_host and account.smtp_password:
                    from src.email_system.sender import EmailSender
                    
                    smtp_config = {
                        'host': account.smtp_host,
                        'port': account.smtp_port,
                        'username': account.smtp_username or account.email_address,
                        'password': account.smtp_password,
                        'use_ssl': account.smtp_port == 465
                    }
                    
                    sender = EmailSender(smtp_config=smtp_config)
                    result = sender.send_email(
                        to_email=e.to_email,
                        subject=e.subject or '(无主题)',
                        body=e.body or '',
                        from_email=e.from_email,
                        from_name=account.account_name,
                        cc_email=e.cc_email,
                        bcc_email=e.bcc_email,
                        html_body=e.html_body,
                        priority=e.priority or 'normal',
                        need_receipt=e.need_receipt or False
                    )
                    
                    if result['success']:
                        logger.info(f"草稿已发送", extra={"email_id": email_id, "to_email": e.to_email})
                        update_data['sent_at'] = datetime.now()
                        # 🔥 设置投递状态为 pending
                        update_data['delivery_status'] = 'pending'
                        account.total_sent += 1
                        db.commit()
                    else:
                        logger.warning(f"发送失败", extra={"email_id": email_id, "error": result['message']})
                        update_data['status'] = 'failed'
                        update_data['internal_notes'] = f"[发送失败] {result['message']}"
                        # 🔥 设置投递状态为 failed
                        update_data['delivery_status'] = 'failed'
                        update_data['bounce_reason'] = result['message']
                else:
                    logger.warning(f"未找到SMTP配置", extra={"email_id": email_id, "from_email": e.from_email})
                    update_data['status'] = 'failed'
                    update_data['internal_notes'] = f"[发送失败] 未找到发件人账户的SMTP配置"
                    # 🔥 设置投递状态为 unknown
                    update_data['delivery_status'] = 'unknown'
            except Exception as ex:
                logger.error(f"发送异常", extra={"email_id": email_id, "error": str(ex)})
                update_data['status'] = 'failed'
                update_data['internal_notes'] = f"[发送异常] {str(ex)}"
                # 🔥 设置投递状态为 failed
                update_data['delivery_status'] = 'failed'
                update_data['bounce_reason'] = str(ex)
    
    # 应用更新
    for k, v in update_data.items():
        setattr(e, k, v)
    
    db.commit()
    db.refresh(e)
    return e


@router.patch("/email_history/{email_id}", response_model=EmailOut)
def patch_email(email_id: int, email_upd: EmailUpdate, db: Session = Depends(get_db)):
    """部分更新邮件（PATCH方法，只更新提供的字段）"""
    import sys
    
    e = db.query(EmailHistory).filter(EmailHistory.id == email_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Email not found")
    
    update_data = email_upd.dict(exclude_unset=True)
    
    # 🔥 PATCH请求日志
    logger.info(f"PATCH邮件", extra={"email_id": email_id, "fields": list(update_data.keys())})
    sys.stdout.flush()
    
    # 🔥 特殊处理：当设置 is_deleted=True 时，自动设置 deleted_at
    if 'is_deleted' in update_data and update_data['is_deleted'] is True:
        if 'deleted_at' not in update_data:
            update_data['deleted_at'] = datetime.now()
            logger.debug(f"自动设置deleted_at", extra={"email_id": email_id})
    
    # 🔥 特殊处理：当恢复邮件时，清空 deleted_at
    if 'is_deleted' in update_data and update_data['is_deleted'] is False:
        update_data['deleted_at'] = None
        update_data['deleted_by'] = None
        logger.debug(f"恢复邮件", extra={"email_id": email_id})
    
    # 应用更新
    for k, v in update_data.items():
        old_value = getattr(e, k, None)
        setattr(e, k, v)
        logger.debug(f"更新字段", extra={"email_id": email_id, "field": k, "old": old_value, "new": v})
        sys.stdout.flush()
    
    db.commit()
    db.refresh(e)
    
    logger.info(f"PATCH邮件成功", extra={"email_id": email_id, "is_deleted": e.is_deleted})
    sys.stdout.flush()
    return e


@router.delete("/email_history/{email_id}")
def delete_email(email_id: int, db: Session = Depends(get_db)):
    """软删除邮件（移入回收站）"""
    e = db.query(EmailHistory).filter(EmailHistory.id == email_id).first()
    if not e:
        logger.warning(f"删除邮件失败: 邮件不存在", extra={"email_id": email_id})
        raise ResourceNotFoundException("邮件不存在", details={"email_id": email_id})
    
    # 软删除：只标记，不真正删除
    logger.warning(f"软删除邮件", extra={"email_id": email_id, "subject": e.subject})
    e.is_deleted = True
    e.deleted_at = datetime.now()
    db.commit()
    
    logger.info(f"邮件已移入回收站", extra={"email_id": email_id})
    return {"deleted": True, "id": email_id, "message": "已移入回收站"}


@router.post("/email_history/{email_id}/restore")
def restore_email(email_id: int, db: Session = Depends(get_db)):
    """恢复已删除的邮件"""
    e = db.query(EmailHistory).filter(
        EmailHistory.id == email_id,
        EmailHistory.is_deleted == True
    ).first()
    
    if not e:
        logger.warning(f"恢复邮件失败: 回收站中无此邮件", extra={"email_id": email_id})
        raise ResourceNotFoundException("回收站中无此邮件", details={"email_id": email_id})
    
    # 恢复邮件
    logger.info(f"恢复邮件", extra={"email_id": email_id, "subject": e.subject})
    e.is_deleted = False
    e.deleted_at = None
    e.deleted_by = None
    db.commit()
    db.refresh(e)
    
    logger.info(f"邮件已恢复", extra={"email_id": email_id})
    return {"restored": True, "id": email_id, "message": "邮件已恢复"}


@router.delete("/email_history/{email_id}/permanent")
def permanent_delete_email(email_id: int, db: Session = Depends(get_db)):
    """永久删除邮件（从数据库中删除）"""
    e = db.query(EmailHistory).filter(
        EmailHistory.id == email_id,
        EmailHistory.is_deleted == True
    ).first()
    
    if not e:
        logger.warning(f"永久删除失败: 回收站中无此邮件", extra={"email_id": email_id})
        raise ResourceNotFoundException("回收站中无此邮件", details={"email_id": email_id})
    
    # 真正删除
    logger.warning(f"永久删除邮件", extra={"email_id": email_id, "subject": e.subject})
    db.delete(e)
    db.commit()
    
    logger.info(f"邮件已永久删除", extra={"email_id": email_id})
    return {"deleted": True, "id": email_id, "message": "邮件已永久删除"}


@router.post("/email_history/empty_trash")
def empty_trash(db: Session = Depends(get_db)):
    """清空回收站（永久删除所有已删除的邮件）"""
    deleted_emails = db.query(EmailHistory).filter(
        EmailHistory.is_deleted == True
    ).all()
    
    count = len(deleted_emails)
    
    logger.warning(f"清空回收站", extra={"count": count})
    for email in deleted_emails:
        db.delete(email)
    
    db.commit()
    
    logger.info(f"回收站已清空", extra={"count": count})
    return {"deleted": True, "count": count, "message": f"已清空回收站，删除了 {count} 封邮件"}


@router.get("/email_history/{email_id}/attachments/{attachment_index}")
def download_attachment(
    email_id: int, 
    attachment_index: int,
    db: Session = Depends(get_db)
):
    """下载邮件附件
    
    Args:
        email_id: 邮件ID
        attachment_index: 附件索引（从0开始）
    """
    # 查询邮件
    email = db.query(EmailHistory).filter(EmailHistory.id == email_id).first()
    if not email:
        logger.warning(f"下载附件失败: 邮件不存在", extra={"email_id": email_id})
        raise ResourceNotFoundException("邮件不存在", details={"email_id": email_id})
    
    if not email.attachments:
        logger.warning(f"下载附件失败: 无附件", extra={"email_id": email_id})
        raise ResourceNotFoundException("该邮件没有附件", details={"email_id": email_id})
    
    # 解析附件数据
    try:
        attachments_str = email.attachments.replace("'", '"')
        attachments = json.loads(attachments_str)
        
        if not isinstance(attachments, list) or attachment_index >= len(attachments):
            logger.warning(f"附件索引无效", extra={"email_id": email_id, "index": attachment_index})
            raise ResourceNotFoundException("附件索引无效", details={"email_id": email_id, "index": attachment_index})
        
        attachment = attachments[attachment_index]
        
        # 获取存储的文件路径
        file_path = attachment.get('file_path')
        if not file_path:
            logger.warning(f"附件文件路径不存在", extra={"email_id": email_id, "index": attachment_index})
            raise ResourceNotFoundException("附件文件不存在", details={"email_id": email_id})
        
        file_path = Path(file_path)
        if not file_path.exists():
            logger.warning(f"附件文件已丢失", extra={"email_id": email_id, "file_path": str(file_path)})
            raise ResourceNotFoundException("附件文件已丢失", details={"email_id": email_id, "file_path": str(file_path)})
        
        # 返回文件
        original_filename = attachment.get('filename', 'attachment')
        logger.info(f"下载附件", extra={"email_id": email_id, "filename": original_filename})
        
        return FileResponse(
            path=str(file_path),
            filename=original_filename,
            media_type=attachment.get('content_type', 'application/octet-stream')
        )
        
    except json.JSONDecodeError as e:
        logger.error(f"附件数据解析失败", extra={"email_id": email_id, "error": str(e)})
        raise BusinessException("附件数据解析失败")
    except Exception as e:
        logger.error(f"下载附件失败", extra={"email_id": email_id, "error": str(e)})
        raise BusinessException(f"下载失败: {str(e)}")


@router.get("/email_history/{email_id}/images/{image_name}")
def get_email_image(
    email_id: int,
    image_name: str,
    db: Session = Depends(get_db)
):
    """获取邮件图片（内嵌图片和外部图片）
    
    Args:
        email_id: 邮件ID
        image_name: 图片文件名（stored_filename）
    """
    # 验证邮件是否存在
    email = db.query(EmailHistory).filter(EmailHistory.id == email_id).first()
    if not email:
        logger.warning(f"获取图片失败: 邮件不存在", extra={"email_id": email_id})
        raise ResourceNotFoundException("邮件不存在", details={"email_id": email_id})
    
    # 图片文件路径
    file_path = Path('attachments') / image_name
    
    if not file_path.exists():
        logger.warning(f"图片文件不存在", extra={"email_id": email_id, "image_name": image_name})
        raise ResourceNotFoundException("图片文件不存在", details={"email_id": email_id, "image_name": image_name})
    
    # 根据文件扩展名判断 MIME 类型
    ext = file_path.suffix.lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml'
    }
    media_type = mime_types.get(ext, 'application/octet-stream')
    
    # 返回图片文件
    logger.debug(f"返回邮件图片", extra={"email_id": email_id, "image_name": image_name})
    return FileResponse(
        path=str(file_path),
        media_type=media_type
    )
