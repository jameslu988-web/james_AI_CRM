from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

from src.crm.database import get_session, EmailHistory
from src.email_system.ai_writer import AIEmailWriter

# 🔥 导入Celery任务（用于异步AI分析）
from src.tasks.ai_tasks import analyze_email_task

router = APIRouter()

# 初始化AI助手
ai_writer = AIEmailWriter()


def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


class EmailAnalysisRequest(BaseModel):
    subject: str
    body: str


class EmailAnalysisResponse(BaseModel):
    category: str
    sentiment: str
    urgency_level: str
    purchase_intent: str
    summary: str
    key_points: List[str]
    suggested_tags: List[str]


class ReplySuggestion(BaseModel):
    title: str
    description: str
    content: str


class PolishRequest(BaseModel):
    content: str
    tone: str = "professional"


class TranslateRequest(BaseModel):
    content: str
    target_lang: str = "en"


# 🔥 新增：生成回复请求模型
class GenerateReplyRequest(BaseModel):
    subject: str
    body: str
    use_knowledge_base: bool = True
    tone: str = "professional"
    model: str = "gpt-4o-mini"  # 🔥 新增：指定使用的 AI 模型
    prompt_template_id: Optional[int] = None  # 🔥 新增：使用指定的提示词模板


@router.post("/ai/analyze", response_model=EmailAnalysisResponse)
def analyze_email(request: EmailAnalysisRequest):
    """AI分析邮件内容"""
    try:
        analysis = ai_writer.analyze_email({
            "subject": request.subject,
            "body": request.body
        })
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.post("/ai/suggest-replies", response_model=List[ReplySuggestion])
def suggest_replies(request: EmailAnalysisRequest):
    """生成智能回复建议"""
    try:
        email_content = {
            "subject": request.subject,
            "body": request.body
        }
        analysis = ai_writer.analyze_email(email_content)
        suggestions = ai_writer.generate_reply_suggestions(email_content, analysis)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成建议失败: {str(e)}")


@router.post("/ai/polish")
def polish_email(request: PolishRequest):
    """润色邮件"""
    try:
        polished = ai_writer.polish_email(request.content, request.tone)
        return {"original": request.content, "polished": polished}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"润色失败: {str(e)}")


@router.post("/ai/translate")
def translate_email(request: TranslateRequest):
    """翻译邮件"""
    try:
        translated = ai_writer.translate_email(request.content, request.target_lang)
        return {"original": request.content, "translated": translated, "target_lang": request.target_lang}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"翻译失败: {str(e)}")


# 🔥 新增：生成AI回复（支持知识库）
@router.post("/ai/generate-reply")
async def generate_reply(request: GenerateReplyRequest, db: Session = Depends(get_db)):
    """生成AI智能回复，支持知识库增强、模型选择和自定义提示词"""
    try:
        # 使用 EmailAIAnalyzer 生成回复
        from src.ai.email_analyzer import get_analyzer
        from src.crm.database import PromptTemplate
        
        analyzer = get_analyzer()
        
        # 🔥 调试日志：打印请求参数
        print(f"\n=== AI生成回复请求 ===")
        print(f"主题: {request.subject}")
        print(f"提示词模板ID: {request.prompt_template_id}")
        print(f"使用知识库: {request.use_knowledge_base}")
        print(f"语气: {request.tone}")
        print(f"模型: {request.model}")
        
        # 🔥 如果指定了提示词模板，使用模板渲染提示词
        custom_prompt = None
        template_used = None
        
        if request.prompt_template_id:
            template = db.query(PromptTemplate).filter(
                PromptTemplate.id == request.prompt_template_id
            ).first()
            
            if not template:
                raise HTTPException(status_code=404, detail="提示词模板不存在")
            
            if not template.is_active:
                raise HTTPException(status_code=400, detail="提示词模板已禁用")
            
            # 🔥 调试日志：打印模板信息
            print(f"✅ 使用模板: {template.name} (ID={template.id})")
            print(f"   系统提示词前50字: {template.system_prompt[:50]}...")
            print(f"   用户提示词前50字: {template.user_prompt_template[:50]}...")
            
            template_used = {
                "id": template.id,
                "name": template.name,
                "recommended_model": template.recommended_model
            }
            
            # 使用模板的推荐模型（如果没有明确指定）
            if request.model == "gpt-4o-mini" and template.recommended_model:
                request.model = template.recommended_model
            
            # 构建自定义提示词
            custom_prompt = {
                "system_prompt": template.system_prompt,
                "user_prompt_template": template.user_prompt_template
            }
        else:
            print("⚠️ 未指定模板，使用默认提示词")
        
        result = await analyzer.generate_reply(
            subject=request.subject,
            body=request.body,
            tone=request.tone,
            model=request.model,  # 🔥 传递模型参数
            use_knowledge_base=request.use_knowledge_base,
            custom_prompt=custom_prompt  # 🔥 传递自定义提示词
        )
        
        # 🔥 如果使用了模板，增加使用次数
        if request.prompt_template_id and result.get('success'):
            template.usage_count = (template.usage_count or 0) + 1
            # 简单的成功率计算
            old_rate = template.success_rate or 0.0
            old_count = (template.usage_count or 1) - 1
            template.success_rate = (old_rate * old_count + 1) / template.usage_count
            db.commit()
        
        # 添加模板信息到返回结果
        if template_used:
            result['template_used'] = template_used
        
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成回复失败: {str(e)}")


@router.post("/ai/analyze-email/{email_id}")
def trigger_ai_analysis(email_id: int, db: Session = Depends(get_db)):
    """🔥 触发AI智能分析（异步任务）"""
    email = db.query(EmailHistory).filter(EmailHistory.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="邮件不存在")
    
    try:
        # 提交异步任务
        task = analyze_email_task.delay(email_id)
        
        return {
            "success": True,
            "email_id": email_id,
            "task_id": task.id,
            "message": "AI分析任务已提交",
            "estimated_time": "3-5秒"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交任务失败: {str(e)}")


@router.get("/ai/analyze-history/{email_id}")
def analyze_history_email(email_id: int, db: Session = Depends(get_db)):
    """分析历史邮件并保存分析结果"""
    email = db.query(EmailHistory).filter(EmailHistory.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="邮件不存在")
    
    try:
        analysis = ai_writer.analyze_email({
            "subject": email.subject or "",
            "body": email.body or ""
        })
        
        # 保存分析结果到数据库
        email.ai_sentiment = analysis.get("sentiment")
        email.ai_summary = analysis.get("summary")
        email.ai_category = analysis.get("category")
        email.urgency_level = analysis.get("urgency_level")
        email.purchase_intent = analysis.get("purchase_intent")
        
        # 保存标签
        import json
        email.tags = json.dumps(analysis.get("suggested_tags", []), ensure_ascii=False)
        
        db.commit()
        db.refresh(email)
        
        return {
            "email_id": email_id,
            "analysis": analysis,
            "saved": True
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.post("/ai/batch-analyze")
def batch_analyze_emails(email_ids: List[int], db: Session = Depends(get_db)):
    """批量分析邮件"""
    results = []
    for email_id in email_ids:
        try:
            result = analyze_history_email(email_id, db)
            results.append(result)
        except Exception as e:
            results.append({"email_id": email_id, "error": str(e)})
    
    return {
        "total": len(email_ids),
        "success": len([r for r in results if "error" not in r]),
        "results": results
    }


@router.get("/ai/extract-actions/{email_id}")
def extract_action_items(email_id: int, db: Session = Depends(get_db)):
    """提取待办事项"""
    email = db.query(EmailHistory).filter(EmailHistory.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="邮件不存在")
    
    try:
        actions = ai_writer.extract_action_items({
            "subject": email.subject or "",
            "body": email.body or ""
        })
        return {"email_id": email_id, "actions": actions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提取失败: {str(e)}")
