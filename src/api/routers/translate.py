"""
翻译API - 提供文本翻译功能
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI
import os
import re

router = APIRouter(prefix="/api", tags=["translate"])


class TranslateRequest(BaseModel):
    text: str
    target_language: str = "zh"  # 默认翻译成中文


class TranslateResponse(BaseModel):
    translated_text: str
    original_text: str
    target_language: str


@router.post("/translate", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    """
    翻译文本内容
    
    参数:
        text: 要翻译的文本（支持HTML格式）
        target_language: 目标语言（zh=中文, en=英文）
    """
    try:
        # 初始化OpenAI客户端
        client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # 构建提示词
        if request.target_language == 'zh':
            target_lang_name = "中文"
        elif request.target_language == 'en':
            target_lang_name = "英文"
        else:
            target_lang_name = request.target_language
        
        prompt = f"""请将以下内容翻译成{target_lang_name}。

要求：
1. 保持原文的格式和结构
2. 如果内容是HTML格式，保留所有HTML标签，只翻译文本内容
3. 专业术语要准确翻译
4. 保持语气和风格
5. 直接返回翻译结果，不要添加任何解释

原文内容：
{request.text}

翻译结果："""
        
        # 调用OpenAI API翻译
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是一个专业的翻译助手，擅长商务邮件和技术文档的翻译。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # 较低的温度以获得更稳定的翻译结果
        )
        
        translated_text = response.choices[0].message.content.strip()
        
        # 清理可能的代码块标记
        translated_text = re.sub(r'^```html\s*', '', translated_text, flags=re.IGNORECASE)
        translated_text = re.sub(r'\s*```$', '', translated_text)
        translated_text = translated_text.strip()
        
        return TranslateResponse(
            translated_text=translated_text,
            original_text=request.text,
            target_language=request.target_language
        )
        
    except Exception as e:
        print(f"❌ 翻译失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"翻译失败: {str(e)}")
