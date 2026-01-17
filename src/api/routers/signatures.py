from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from src.crm.database import get_session, EmailSignature
from .auth import get_current_user

router = APIRouter(prefix="/api/signatures", tags=["signatures"])

# 数据库连接 - 使用PostgreSQL
def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


class SignatureCreate(BaseModel):
    name: str
    content: str
    is_default: bool = False


class SignatureUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    is_default: Optional[bool] = None


class SignatureResponse(BaseModel):
    id: int
    user_id: int
    name: str
    content: str
    is_default: bool
    display_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("") # , response_model=List[SignatureResponse])
async def get_signatures(
    response: Response,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的所有签名"""
    try:
        print(f"\n=== 获取签名列表 ===")
        print(f"用户ID: {current_user.id}, 用户名: {current_user.username}")
        
        # 获取签名列表
        signatures = db.query(EmailSignature).filter(
            EmailSignature.user_id == current_user.id
        ).order_by(EmailSignature.display_order, EmailSignature.id).all()
        
        print(f"查询到 {len(signatures)} 个签名")
        
        total = len(signatures)
        
        # 设置 Content-Range 响应头（React Admin 必须）
        response.headers["Content-Range"] = f"signatures 0-{total-1 if total > 0 else 0}/{total}"
        response.headers["Access-Control-Expose-Headers"] = "Content-Range"
        
        # 手动转换为JSON可序列化格式
        result = []
        for sig in signatures:
            result.append({
                "id": sig.id,
                "user_id": sig.user_id,
                "name": sig.name,
                "content": sig.content,
                "is_default": sig.is_default,
                "display_order": sig.display_order,
                "created_at": sig.created_at.isoformat() if sig.created_at else None,
                "updated_at": sig.updated_at.isoformat() if sig.updated_at else None
            })
        
        print(f"=== 返回签名列表 ===\n")
        return result
    except Exception as e:
        import traceback
        print(f"\n=== 签名 API 错误 ===")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        traceback.print_exc()
        print(f"=== 错误结束 ===\n")
        raise HTTPException(status_code=500, detail=f"获取签名列表失败: {str(e)}")


@router.post("", response_model=SignatureResponse)
async def create_signature(
    signature: SignatureCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新签名"""
    try:
        print(f"Creating signature for user {current_user.id}: {signature.name}")
        
        # 如果设置为默认，先取消其他默认签名
        if signature.is_default:
            db.query(EmailSignature).filter(
                EmailSignature.user_id == current_user.id
            ).update({"is_default": False})
        
        # 获取最大的display_order
        max_order = db.query(EmailSignature.display_order).filter(
            EmailSignature.user_id == current_user.id
        ).order_by(EmailSignature.display_order.desc()).first()
        
        next_order = (max_order[0] if max_order else 0) + 1
        
        # 创建新签名
        new_signature = EmailSignature(
            user_id=current_user.id,
            name=signature.name,
            content=signature.content,
            is_default=signature.is_default,
            display_order=next_order
        )
        db.add(new_signature)
        db.commit()
        db.refresh(new_signature)
        
        print(f"Signature created successfully: ID={new_signature.id}")
        return new_signature
    except Exception as e:
        db.rollback()
        print(f"Error creating signature: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"创建签名失败: {str(e)}")


@router.get("/{signature_id}", response_model=SignatureResponse)
async def get_signature(
    signature_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个签名"""
    signature = db.query(EmailSignature).filter(
        EmailSignature.id == signature_id,
        EmailSignature.user_id == current_user.id
    ).first()
    
    if not signature:
        raise HTTPException(status_code=404, detail="签名不存在")
    
    return signature


@router.put("/{signature_id}", response_model=SignatureResponse)
async def update_signature(
    signature_id: int,
    signature: SignatureUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新签名"""
    print(f"\n=== Updating signature {signature_id} ===")
    print(f"Received data: name={signature.name}, content_length={len(signature.content) if signature.content else 0}, is_default={signature.is_default}")
    
    # 查找签名
    db_signature = db.query(EmailSignature).filter(
        EmailSignature.id == signature_id,
        EmailSignature.user_id == current_user.id
    ).first()
    
    if not db_signature:
        raise HTTPException(status_code=404, detail="签名不存在")
    
    print(f"Existing signature: name={db_signature.name}, content_length={len(db_signature.content) if db_signature.content else 0}")
    
    # 如果设置为默认，先取消其他默认签名
    if signature.is_default:
        db.query(EmailSignature).filter(
            EmailSignature.user_id == current_user.id,
            EmailSignature.id != signature_id
        ).update({"is_default": False})
    
    # 更新字段
    if signature.name is not None:
        db_signature.name = signature.name
        print(f"Updating name to: {signature.name}")
    if signature.content is not None:
        db_signature.content = signature.content
        print(f"Updating content (length: {len(signature.content)})")
    if signature.is_default is not None:
        db_signature.is_default = signature.is_default
        print(f"Updating is_default to: {signature.is_default}")
    
    db.commit()
    db.refresh(db_signature)
    
    print(f"Updated signature: name={db_signature.name}, content_length={len(db_signature.content) if db_signature.content else 0}")
    print(f"=== Update complete ===\n")
    
    return db_signature


@router.delete("/{signature_id}")
async def delete_signature(
    signature_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除签名"""
    # 查找签名
    db_signature = db.query(EmailSignature).filter(
        EmailSignature.id == signature_id,
        EmailSignature.user_id == current_user.id
    ).first()
    
    if not db_signature:
        raise HTTPException(status_code=404, detail="签名不存在")
    
    # 删除签名
    db.delete(db_signature)
    db.commit()
    
    return {"message": "签名已删除"}


@router.get("/default/get", response_model=SignatureResponse | None)
async def get_default_signature(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取默认签名"""
    signature = db.query(EmailSignature).filter(
        EmailSignature.user_id == current_user.id,
        EmailSignature.is_default == True
    ).first()
    
    return signature
