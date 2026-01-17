"""
AI 邮件分析器
使用 aihubmix.com API 进行邮件智能分析
"""

import os
import json
import traceback
from typing import Dict, Optional, List
import httpx
from datetime import datetime


class EmailAIAnalyzer:
    """邮件 AI 分析器"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        """
        初始化 AI 分析器
        
        参数:
            api_key: aihubmix.com API Key
            base_url: API 基础 URL
        """
        self.api_key = api_key or os.getenv('AIHUBMIX_API_KEY', 'sk-5dn0RF7nn31mpHNjEfC5Ca1579F447418aE48e7b0d8b18F7')
        self.base_url = base_url or os.getenv('AIHUBMIX_BASE_URL', 'https://aihubmix.com/v1')
        self.timeout = 30.0
        
    async def analyze_email(
        self, 
        subject: str, 
        body: str,
        from_email: str = None,
        model: str = "gpt-4o-mini"
    ) -> Dict:
        """
        分析邮件内容
        
        参数:
            subject: 邮件主题
            body: 邮件正文
            from_email: 发件人邮箱
            model: AI 模型名称
            
        返回:
            分析结果字典
        """
        try:
            # 构建分析提示词
            prompt = self._build_analysis_prompt(subject, body, from_email)
            
            # 调用 AI API
            result = await self._call_api(prompt, model)
            
            # 解析结果
            analysis = self._parse_analysis_result(result)
            
            return {
                "success": True,
                "analysis": analysis,
                "model": model,
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ AI 分析失败: {str(e)}")
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "analysis": self._get_default_analysis()
            }
    
    def _build_analysis_prompt(self, subject: str, body: str, from_email: str = None) -> str:
        """构建分析提示词（严格按照系统方案）"""
        
        prompt = f"""你是一个专业的外贸邮件AI智能分析引擎。请深度分析以下邮件，严格按照外贸业务流程进行多维度评估。

【邮件信息】
主题: {subject}
正文: {body}
"""
        if from_email:
            prompt += f"发件人: {from_email}\n"
        
        prompt += """

请进行全面的智能分析并返回以下JSON格式结果（只返回JSON，不要其他解释）：

{
  "业务阶段分类": {
    "primary_stage": "新客询盘|报价跟进|样品阶段|谈判议价|订单确认|生产跟踪|售后服务|老客维护|垃圾营销",
    "secondary_category": "产品信息|价格询问|定制需求|样品申请|认证资质|物流运输|付款方式|起订量|售后问题"
  },
  
  "客户意图识别": {
    "purchase_intent": "high|medium|low",
    "purchase_intent_score": 0-100,
    "budget_level": "高端|中端|低端",
    "urgency": "急单|常规|长期计划",
    "decision_authority": "决策者|采购经理|采购员|询价员",
    "competition_status": "独家询价|2-3家比价|多家比价|价格敏感",
    "customer_business_type": "批发商|零售商|品牌商|贸易公司|电商|终端用户"
  },
  
  "情感与态度": {
    "sentiment": "positive|neutral|negative|urgent|complaint",
    "tone": "专业|随意|急躁|礼貌|强硬",
    "satisfaction_level": "满意|中立|不满|投诉"
  },
  
  "紧急度评估": {
    "urgency_level": "high|medium|low",
    "requires_urgent_response": true|false,
    "response_deadline": "1小时内|4小时内|24小时内|3天内",
    "business_impact": "critical|important|normal|low"
  },
  
  "客户画像推断": {
    "customer_type": "新客户|老客户|潜在大客户|低价值客户|未知",
    "customer_grade_suggestion": "A级（大客户）|B级（成长型）|C级（潜力客户）|D级（普通询盘）",
    "professionalism": "专业买家|新手|中间商|直接客户",
    "communication_style": "简洁高效|详细沟通|正式严谨|友好随和"
  },
  
  "内容分析": {
    "summary": "邮件核心内容摘要（50字内）",
    "key_points": ["关键信息点1", "关键信息点2", "关键信息点3"],
    "mentioned_products": ["提及的产品"],
    "mentioned_quantities": "数量信息",
    "mentioned_prices": "价格相关",
    "mentioned_timeline": "时间要求",
    "questions_asked": ["客户提出的问题"],
    "concerns": ["客户的顾虑"]
  },
  
  "行动建议": {
    "next_action": "具体的下一步操作建议",
    "response_template_suggestion": "首次询盘回复|报价单|样品确认|订单确认|售后处理|跟进邮件",
    "suggested_tags": ["业务标签1", "业务标签2"],
    "follow_up_date": "建议跟进时间（天数）",
    "requires_human_review": true|false,
    "human_review_reason": "需要人工审核的原因"
  },
  
  "风险与机会": {
    "risk_level": "high|medium|low",
    "risk_factors": ["风险因素"],
    "opportunity_score": 0-100,
    "conversion_probability": 0-100,
    "estimated_order_value": "预估订单金额"
  }
}

【分析要点】
1. 根据邮件内容判断客户处于哪个业务阶段
2. 深度分析客户的购买意向强度（通过语气、细节问题、紧迫性判断）
3. 识别客户的决策权限和采购专业度
4. 评估是否存在竞争对手
5. 推断客户预算水平（高端/中端/低端）
6. 提取所有关键业务信息（产品、数量、价格、时间）
7. 给出个性化的回复策略和行动建议
8. 标注是否需要人工介入（大额订单、投诉、复杂需求）

请确保返回的是纯JSON格式，不要包含markdown符号。
"""
        return prompt
    
    async def _call_api(self, prompt: str, model: str) -> str:
        """调用 aihubmix.com API"""
        
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            return content
    
    def _parse_analysis_result(self, result: str) -> Dict:
        """解析 AI 返回的分析结果（兼容复杂结构）"""
        
        try:
            # 清理可能的 markdown 代码块标记
            result = result.strip()
            if result.startswith("```json"):
                result = result[7:]
            if result.startswith("```"):
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
            
            # 解析 JSON
            analysis = json.loads(result)
            
            # 将新结构平坦化为兼容格式（保持与数据库字段一致）
            flattened = {}
            
            # 业务阶段
            if "业务阶段分类" in analysis:
                flattened["business_stage"] = analysis["业务阶段分类"].get("primary_stage", "")
                flattened["category"] = self._map_stage_to_category(flattened["business_stage"])
                flattened["secondary_category"] = analysis["业务阶段分类"].get("secondary_category", "")
            
            # 客户意图
            if "客户意图识别" in analysis:
                intent = analysis["客户意图识别"]
                flattened["purchase_intent"] = intent.get("purchase_intent", "low")
                flattened["purchase_intent_score"] = intent.get("purchase_intent_score", 0)
                flattened["budget_level"] = intent.get("budget_level", "")
                flattened["urgency"] = intent.get("urgency", "")
                flattened["decision_authority"] = intent.get("decision_authority", "")
                flattened["competition_status"] = intent.get("competition_status", "")
                flattened["customer_business_type"] = intent.get("customer_business_type", "")
            
            # 情感态度
            if "情感与态度" in analysis:
                emotion = analysis["情感与态度"]
                flattened["sentiment"] = emotion.get("sentiment", "neutral")
                flattened["tone"] = emotion.get("tone", "")
                flattened["satisfaction_level"] = emotion.get("satisfaction_level", "")
            
            # 紧急度
            if "紧急度评估" in analysis:
                urgency = analysis["紧急度评估"]
                flattened["urgency_level"] = urgency.get("urgency_level", "medium")
                flattened["requires_urgent_response"] = urgency.get("requires_urgent_response", False)
                flattened["response_deadline"] = urgency.get("response_deadline", "")
                flattened["business_impact"] = urgency.get("business_impact", "")
            
            # 客户画像
            if "客户画像推断" in analysis:
                profile = analysis["客户画像推断"]
                flattened["customer_type"] = profile.get("customer_type", "未知")
                flattened["customer_grade_suggestion"] = profile.get("customer_grade_suggestion", "")
                flattened["professionalism"] = profile.get("professionalism", "")
                flattened["communication_style"] = profile.get("communication_style", "")
            
            # 内容分析
            if "内容分析" in analysis:
                content = analysis["内容分析"]
                flattened["summary"] = content.get("summary", "")
                flattened["key_points"] = content.get("key_points", [])
                flattened["mentioned_products"] = content.get("mentioned_products", [])
                flattened["mentioned_quantities"] = content.get("mentioned_quantities", "")
                flattened["mentioned_prices"] = content.get("mentioned_prices", "")
                flattened["mentioned_timeline"] = content.get("mentioned_timeline", "")
                flattened["questions_asked"] = content.get("questions_asked", [])
                flattened["concerns"] = content.get("concerns", [])
            
            # 行动建议
            if "行动建议" in analysis:
                action = analysis["行动建议"]
                flattened["next_action"] = action.get("next_action", "")
                flattened["response_template_suggestion"] = action.get("response_template_suggestion", "")
                flattened["suggested_tags"] = action.get("suggested_tags", [])
                flattened["follow_up_date"] = action.get("follow_up_date", "")
                flattened["requires_human_review"] = action.get("requires_human_review", False)
                flattened["human_review_reason"] = action.get("human_review_reason", "")
            
            # 风险机会
            if "风险与机会" in analysis:
                risk = analysis["风险与机会"]
                flattened["risk_level"] = risk.get("risk_level", "low")
                flattened["risk_factors"] = risk.get("risk_factors", [])
                flattened["opportunity_score"] = risk.get("opportunity_score", 0)
                flattened["conversion_probability"] = risk.get("conversion_probability", 0)
                flattened["estimated_order_value"] = risk.get("estimated_order_value", "")
            
            # 保留原始完整数据
            flattened["full_analysis"] = analysis
            
            # 确保基本字段存在（与数据库字段对应）
            required_fields = ['sentiment', 'category', 'urgency_level', 'purchase_intent', 'summary']
            for field in required_fields:
                if field not in flattened:
                    flattened[field] = 'unknown'
            
            return flattened
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {str(e)}")
            print(f"原始结果: {result}")
            return self._get_default_analysis()
    
    def _map_stage_to_category(self, stage: str) -> str:
        """将业务阶段映射到简单分类（兼容数据库）"""
        mapping = {
            "新客询盘": "inquiry",
            "报价跟进": "quotation",
            "样品阶段": "sample",
            "谈判议价": "quotation",
            "订单确认": "order",
            "生产跟踪": "order",
            "售后服务": "complaint",
            "老客维护": "follow_up",
            "垃圾营销": "spam"
        }
        return mapping.get(stage, "spam")  # 默认为垃圾营销
    
    def _get_default_analysis(self) -> Dict:
        """获取默认分析结果（当 AI 分析失败时）"""
        return {
            "sentiment": "neutral",
            "category": "spam",  # 改为spam（垃圾营销）
            "urgency_level": "medium",
            "purchase_intent": "low",
            "summary": "AI 分析失败，需要人工处理",
            "key_points": [],
            "suggested_tags": [],
            "next_action": "人工审核邮件",
            "customer_type": "未知",
            "requires_urgent_response": False
        }
    
    async def generate_reply(
        self,
        subject: str,
        body: str,
        context: Dict = None,
        tone: str = "professional",
        model: str = "gpt-4o-mini",
        use_knowledge_base: bool = True,
        custom_prompt: Dict = None  # 🔥 新增：自定义提示词
    ) -> Dict:
        """
        生成智能回复
        
        参数:
            subject: 原邮件主题
            body: 原邮件正文
            context: 上下文信息（客户信息、历史邮件等）
            tone: 回复语气 (professional/friendly/formal)
            model: AI 模型
            use_knowledge_base: 是否使用向量知识库
            custom_prompt: 自定义提示词（包含 system_prompt 和 user_prompt_template）
            
        返回:
            回复内容字典
        """
        try:
            # 🔥 新增：如果启用知识库，先检索相关知识
            knowledge_context = None
            if use_knowledge_base:
                knowledge_context = await self._search_knowledge(subject, body)
            
            # 🔥 使用自定义提示词或默认提示词
            if custom_prompt:
                prompt = self._build_custom_prompt(
                    subject,
                    body,
                    context,
                    tone,
                    knowledge_context,
                    custom_prompt
                )
            else:
                prompt = self._build_reply_prompt(
                    subject, 
                    body, 
                    context, 
                    tone,
                    knowledge_context
                )
            
            result = await self._call_api(prompt, model)
            
            # 🔥 清理AI返回的内容，移除HTML文档标签
            cleaned_result = self._clean_html_response(result)
            
            return {
                "success": True,
                "reply": cleaned_result,
                "model": model,
                "knowledge_used": knowledge_context is not None and len(knowledge_context) > 0,
                "knowledge_context": knowledge_context or [],  # 🔥 返回知识库上下文
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 生成回复失败: {str(e)}")
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "reply": ""
            }
    
    async def _search_knowledge(self, subject: str, body: str) -> Optional[List[Dict]]:
        """
        从向量知识库中搜索相关知识
        
        参数:
            subject: 邮件主题
            body: 邮件正文
            
        返回:
            相关知识片段列表
        """
        try:
            from src.ai.vector_knowledge import VectorKnowledgeService
            from src.crm.database import get_session
            
            vector_service = VectorKnowledgeService()
            db = get_session()
            
            try:
                # 组合查询文本
                query_text = f"{subject}\n{body}"
                
                # 搜索相关知识（前3条）
                results = await vector_service.search_similar(
                    query=query_text,
                    limit=3,
                    db_session=db
                )
                
                if results:
                    print(f"✅ 从知识库检索到 {len(results)} 条相关知识")
                    return results
                else:
                    print("⚠️ 知识库未检索到相关内容")
                    return None
                    
            finally:
                db.close()
                
        except Exception as e:
            print(f"⚠️ 知识库检索失败: {str(e)}")
            return None
    
    def _clean_html_response(self, html_content: str) -> str:
        """
        清理AI返回的HTML内容，移除多余的文档标签
        
        参数:
            html_content: AI生成的HTML内容
            
        返回:
            清理后的HTML内容
        """
        import re
        
        # 移除HTML文档声明和<html>标签
        content = html_content.strip()
        
        # 移除<!DOCTYPE>
        content = re.sub(r'<!DOCTYPE[^>]*>', '', content, flags=re.IGNORECASE)
        
        # 移除<html>标签（包括属性）
        content = re.sub(r'<html[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'</html>', '', content, flags=re.IGNORECASE)
        
        # 移除<head>部分
        content = re.sub(r'<head>.*?</head>', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # 移除<body>标签但保留内容
        content = re.sub(r'<body[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'</body>', '', content, flags=re.IGNORECASE)
        
        # 移除开头的```html和结尾的```（Markdown代码块）
        content = re.sub(r'^```html\s*', '', content, flags=re.IGNORECASE)
        content = re.sub(r'\s*```$', '', content)
        
        # 清理多余的空白
        content = content.strip()
        
        return content
    
    def _build_reply_prompt(
        self, 
        subject: str, 
        body: str, 
        context: Dict = None,
        tone: str = "professional",
        knowledge_context: Optional[List[Dict]] = None
    ) -> str:
        """构建回复生成提示词"""
        
        prompt = f"""你是一个专业的外贸业务员。请根据收到的客户邮件，生成一封专业的英文回复邮件。

原邮件信息：
主题: {subject}
正文: {body}

"""
        if context:
            if context.get('customer_name'):
                prompt += f"客户姓名: {context['customer_name']}\n"
            if context.get('company_name'):
                prompt += f"公司名称: {context['company_name']}\n"
            if context.get('history'):
                prompt += f"往来历史: {context['history']}\n"
        
        # 🔥 新增：添加知识库上下文
        if knowledge_context:
            prompt += "\n相关知识库信息：\n"
            for idx, knowledge in enumerate(knowledge_context, 1):
                prompt += f"{idx}. {knowledge['content'][:300]}...\n"
            prompt += "\n请参考以上知识库信息来生成回复。\n"
        
        tone_desc = {
            "professional": "专业、礼貌",
            "friendly": "友好、亲切", 
            "formal": "正式、严谨",
            "enthusiastic": "热情、积极"  # 🔥 新增
        }
        
        prompt += f"""
回复要求：
1. 语气：{tone_desc.get(tone, '专业')}
2. 语言：使用流利的英文
3. 格式：**使用HTML格式**，使用<p>标签分段，使用<br>换行
4. 内容：针对客户的问题给出专业回复
5. 结构：
   - 开头：专业的问候语（Dear XXX,）
   - 正文：使用<p>标签将不同主题分成多个段落
   - 列表：如果有多个要点，使用<ul><li>或编号列表
   - 结尾：专业的结束语（Best regards, Sincerely等）和完整签名块
6. 签名格式：
   ```
   <p>Best regards,</p>
   <p>
   [Your Name]<br>
   [Your Position]<br>
   [Your Company]<br>
   Email: sales@underwearexport.com<br>
   WhatsApp: +86 138 xxxx xxxx
   </p>
   ```

**重要**: 
- 每个段落必须用<p>标签包裹
- 段落之间会自动有间距
- 不要将所有内容挤在一个段落中
- **不要生成完整的HTML文档结构（不要包含<!DOCTYPE>, <html>, <head>, <body>等标签）**
- **直接生成邮件正文的HTML片段，从Dear开头即可**
- 不要包含"Subject:"等标记

请直接生成HTML格式的邮件正文片段（不要包含文档声明和标签）。
"""
        return prompt
    
    def _build_custom_prompt(
        self,
        subject: str,
        body: str,
        context: Dict = None,
        tone: str = "professional",
        knowledge_context: Optional[List[Dict]] = None,
        custom_prompt: Dict = None
    ) -> str:
        """🔥 使用自定义模板构建提示词"""
        
        # 构建变量字典
        tone_desc = {
            "professional": "专业、礼貌",
            "friendly": "友好、亲切",
            "formal": "正式、严谨",
            "enthusiastic": "热情、积极"
        }
        
        # 构建知识库上下文字符串
        knowledge_str = ""
        if knowledge_context:
            knowledge_str = "\n相关知识库信息：\n"
            for idx, knowledge in enumerate(knowledge_context, 1):
                knowledge_str += f"{idx}. {knowledge['content'][:300]}...\n"
            knowledge_str += "\n请参考以上知识库信息来生成回复。\n"
        
        # 构建客户上下文字符串
        customer_str = ""
        if context:
            if context.get('customer_name'):
                customer_str += f"客户姓名: {context['customer_name']}\n"
            if context.get('company_name'):
                customer_str += f"公司名称: {context['company_name']}\n"
            if context.get('history'):
                customer_str += f"往来历史: {context['history']}\n"
        
        # 渲染模板
        variables = {
            "subject": subject,
            "body": body,
            "tone_desc": tone_desc.get(tone, "专业"),
            "knowledge_context": knowledge_str,
            "customer_context": customer_str
        }
        
        try:
            # 渲染用户提示词模板
            user_prompt = custom_prompt['user_prompt_template'].format(**variables)
            
            # 如果有系统提示词，拼接起来
            if custom_prompt.get('system_prompt'):
                final_prompt = f"{custom_prompt['system_prompt']}\n\n{user_prompt}"
            else:
                final_prompt = user_prompt
            
            return final_prompt
            
        except KeyError as e:
            # 如果模板变量错误，回退到默认提示词
            print(f"⚠️ 模板变量错误: {e}，使用默认提示词")
            return self._build_reply_prompt(subject, body, context, tone, knowledge_context)


# 全局实例
_analyzer_instance = None

def get_analyzer() -> EmailAIAnalyzer:
    """获取 AI 分析器单例"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = EmailAIAnalyzer()
    return _analyzer_instance
