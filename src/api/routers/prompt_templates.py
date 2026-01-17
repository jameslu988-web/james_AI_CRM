"""
提示词模板管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.crm.database import get_session, PromptTemplate
from src.api.schemas import PromptTemplateCreate, PromptTemplateUpdate, PromptTemplateOut
import json

router = APIRouter()


def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@router.get("/prompt-templates", response_model=List[PromptTemplateOut])
def get_prompt_templates(
    template_type: Optional[str] = Query(None, description="模板类型过滤：reply/analysis/polish"),
    is_active: Optional[bool] = Query(None, description="是否只返回启用的模板"),
    db: Session = Depends(get_db)
):
    """获取提示词模板列表"""
    query = db.query(PromptTemplate)
    
    if template_type:
        query = query.filter(PromptTemplate.template_type == template_type)
    
    if is_active is not None:
        query = query.filter(PromptTemplate.is_active == is_active)
    
    templates = query.order_by(PromptTemplate.is_default.desc(), PromptTemplate.id.asc()).all()
    return templates


@router.get("/prompt-templates/{template_id}", response_model=PromptTemplateOut)
def get_prompt_template(template_id: int, db: Session = Depends(get_db)):
    """获取单个提示词模板"""
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    return template


@router.post("/prompt-templates", response_model=PromptTemplateOut)
def create_prompt_template(template: PromptTemplateCreate, db: Session = Depends(get_db)):
    """创建新的提示词模板"""
    
    # 如果设置为默认，取消同类型的其他默认模板
    if template.is_default:
        db.query(PromptTemplate).filter(
            PromptTemplate.template_type == template.template_type,
            PromptTemplate.is_default == True
        ).update({"is_default": False})
    
    # 创建新模板
    db_template = PromptTemplate(**template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return db_template


@router.put("/prompt-templates/{template_id}", response_model=PromptTemplateOut)
def update_prompt_template(
    template_id: int,
    template: PromptTemplateUpdate,
    db: Session = Depends(get_db)
):
    """更新提示词模板"""
    db_template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    
    if not db_template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 更新字段
    update_data = template.model_dump(exclude_unset=True)
    
    # 如果设置为默认，取消同类型的其他默认模板
    if update_data.get('is_default'):
        db.query(PromptTemplate).filter(
            PromptTemplate.template_type == db_template.template_type,
            PromptTemplate.is_default == True,
            PromptTemplate.id != template_id
        ).update({"is_default": False})
    
    for key, value in update_data.items():
        setattr(db_template, key, value)
    
    db.commit()
    db.refresh(db_template)
    
    return db_template


@router.delete("/prompt-templates/{template_id}")
def delete_prompt_template(template_id: int, db: Session = Depends(get_db)):
    """删除提示词模板"""
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 如果是默认模板，不允许删除
    if template.is_default:
        raise HTTPException(status_code=400, detail="默认模板不允许删除，请先取消默认设置")
    
    db.delete(template)
    db.commit()
    
    return {"success": True, "message": "模板已删除"}


@router.post("/prompt-templates/{template_id}/set-default")
def set_default_template(template_id: int, db: Session = Depends(get_db)):
    """设置为默认模板"""
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 取消同类型的其他默认模板
    db.query(PromptTemplate).filter(
        PromptTemplate.template_type == template.template_type,
        PromptTemplate.is_default == True
    ).update({"is_default": False})
    
    # 设置为默认
    template.is_default = True
    db.commit()
    
    return {"success": True, "message": f"已设置 {template.name} 为默认模板"}


@router.post("/prompt-templates/{template_id}/increment-usage")
def increment_template_usage(template_id: int, success: bool = True, db: Session = Depends(get_db)):
    """增加模板使用次数并更新成功率"""
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 更新使用次数
    old_count = template.usage_count or 0
    template.usage_count = old_count + 1
    
    # 更新成功率（简单加权平均）
    if success:
        old_rate = template.success_rate or 0.0
        template.success_rate = (old_rate * old_count + 1) / template.usage_count
    else:
        old_rate = template.success_rate or 0.0
        template.success_rate = (old_rate * old_count) / template.usage_count
    
    db.commit()
    
    return {"success": True, "usage_count": template.usage_count, "success_rate": template.success_rate}


@router.get("/prompt-templates/{template_id}/preview")
def preview_prompt(
    template_id: int,
    subject: str = Query(..., description="邮件主题"),
    body: str = Query(..., description="邮件正文"),
    tone: str = Query("professional", description="语气"),
    db: Session = Depends(get_db)
):
    """预览渲染后的提示词"""
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 构建变量字典
    tone_desc = {
        "professional": "专业、礼貌",
        "friendly": "友好、亲切",
        "formal": "正式、严谨",
        "enthusiastic": "热情、积极"
    }
    
    variables = {
        "subject": subject,
        "body": body,
        "tone_desc": tone_desc.get(tone, "专业"),
        "knowledge_context": "[知识库内容将在实际使用时插入]",
        "customer_context": "[客户上下文将在实际使用时插入]"
    }
    
    # 渲染提示词
    try:
        rendered_prompt = template.user_prompt_template.format(**variables)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"模板变量错误: {str(e)}")
    
    return {
        "template_id": template_id,
        "template_name": template.name,
        "system_prompt": template.system_prompt,
        "rendered_prompt": rendered_prompt,
        "recommended_model": template.recommended_model
    }
