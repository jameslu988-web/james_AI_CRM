import os
import json
import re
from typing import Dict, List, Optional
from openai import OpenAI  # 🔥 引入 OpenAI 客户端


class AIEmailWriter:
    """AI邮件智能助手 - 提供邮件分析、生成、润色等功能"""
    
    def __init__(self):
        # 🔥 初始化 OpenAI 客户端
        self.api_key = os.getenv('AIHUBMIX_API_KEY', 'sk-5dn0RF7nn31mpHNjEfC5Ca1579F447418aE48e7b0d8b18F7')
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=os.getenv('AIHUBMIX_BASE_URL', 'https://aihubmix.com/v1')
        )
    
    def generate_cold_email(self, prospect_data: dict) -> str:
        """生成开发信"""
        company = prospect_data.get("company_name") or prospect_data.get("company") or "your company"
        contact = prospect_data.get("contact_name") or prospect_data.get("name") or "there"
        website = prospect_data.get("website") or ""
        industry = prospect_data.get("industry") or "apparel"
        return (
            f"Hi {contact},\n\n"
            f"I noticed {company} in the {industry} space{(' (' + website + ')') if website else ''}. "
            "We manufacture premium men's underwear with low MOQ, consistent quality, and fast lead times. "
            "We support private label, flexible materials, and quick sampling.\n\n"
            "Would you be open to reviewing a short catalog or a sample kit this week? "
            "Happy to share pricing tiers and lead time estimates tailored to your needs.\n\n"
            "Best regards,\n"
            "John | Underwear Export Team"
        )
    
    def analyze_email(self, email_content: dict) -> dict:
        """
        AI邮件分析 - 分析邮件内容并提取关键信息
        
        Args:
            email_content: {"subject": "...", "body": "..."}
            
        Returns:
            {
                "category": "inquiry/quotation/order/complaint/follow_up/sample",
                "sentiment": "positive/neutral/negative/urgent",
                "urgency_level": "high/medium/low",
                "purchase_intent": "high/medium/low",
                "summary": "邮件摘要",
                "key_points": ["关键点1", "关键点2"],
                "suggested_tags": ["询价", "紧急"]
            }
        """
        subject = email_content.get("subject", "").lower()
        body = email_content.get("body", "").lower()
        combined = f"{subject} {body}"
        
        # 简单规则引擎（实际应用中可接入OpenAI GPT）
        result = {
            "category": self._detect_category(combined),
            "sentiment": self._detect_sentiment(combined),
            "urgency_level": self._detect_urgency(combined),
            "purchase_intent": self._detect_intent(combined),
            "summary": self._generate_summary(email_content),
            "key_points": self._extract_key_points(combined),
            "suggested_tags": []
        }
        
        # 生成建议标签
        result["suggested_tags"] = self._suggest_tags(result)
        
        return result
    
    def _detect_category(self, text: str) -> str:
        """检测邮件类别"""
        if any(word in text for word in ["quote", "price", "quotation", "询价", "报价"]):
            return "inquiry"
        elif any(word in text for word in ["order", "purchase", "buy", "订单", "采购"]):
            return "order"
        elif any(word in text for word in ["sample", "样品", "样衣"]):
            return "sample"
        elif any(word in text for word in ["complain", "issue", "problem", "投诉", "问题"]):
            return "complaint"
        elif any(word in text for word in ["follow", "update", "status", "跟进"]):
            return "follow_up"
        else:
            return "spam"  # 默认为垃圾营销
    
    def _detect_sentiment(self, text: str) -> str:
        """检测情绪"""
        if any(word in text for word in ["urgent", "asap", "immediately", "紧急", "尽快", "立即"]):
            return "urgent"
        elif any(word in text for word in ["angry", "disappointed", "unacceptable", "生气", "失望"]):
            return "negative"
        elif any(word in text for word in ["thank", "great", "excellent", "perfect", "感谢", "很好"]):
            return "positive"
        else:
            return "neutral"
    
    def _detect_urgency(self, text: str) -> str:
        """检测紧急程度"""
        if any(word in text for word in ["urgent", "asap", "emergency", "immediately", "紧急", "马上"]):
            return "high"
        elif any(word in text for word in ["soon", "quickly", "尽快"]):
            return "medium"
        else:
            return "low"
    
    def _detect_intent(self, text: str) -> str:
        """检测购买意向"""
        high_intent_words = ["order", "purchase", "buy", "payment", "deposit", "订单", "购买", "付款"]
        medium_intent_words = ["quote", "price", "sample", "询价", "报价", "样品"]
        
        if any(word in text for word in high_intent_words):
            return "high"
        elif any(word in text for word in medium_intent_words):
            return "medium"
        else:
            return "low"
    
    def _generate_summary(self, email_content: dict) -> str:
        """生成邮件摘要（简化版）"""
        body = email_content.get("body", "")
        # 简单截取前200字符作为摘要
        summary = body[:200].strip()
        if len(body) > 200:
            summary += "..."
        return summary
    
    def _extract_key_points(self, text: str) -> List[str]:
        """提取关键点"""
        key_points = []
        
        # 提取数量
        qty_match = re.search(r'(\d+)\s*(pcs|pieces|units|件)', text, re.IGNORECASE)
        if qty_match:
            key_points.append(f"数量: {qty_match.group(1)} {qty_match.group(2)}")
        
        # 提取价格
        price_match = re.search(r'\$\s*([\d.]+)', text)
        if price_match:
            key_points.append(f"价格: ${price_match.group(1)}")
        
        # 提取日期
        date_patterns = [r'\d{4}[-/]\d{1,2}[-/]\d{1,2}', r'\d{1,2}[-/]\d{1,2}[-/]\d{4}']
        for pattern in date_patterns:
            date_match = re.search(pattern, text)
            if date_match:
                key_points.append(f"日期: {date_match.group(0)}")
                break
        
        return key_points if key_points else ["无关键数据"]
    
    def _suggest_tags(self, analysis: dict) -> List[str]:
        """根据分析结果建议标签"""
        tags = []
        
        # 类别标签
        category_map = {
            "inquiry": "询价",
            "order": "订单",
            "sample": "样品",
            "complaint": "投诉",
            "follow_up": "跟进"
        }
        if analysis["category"] in category_map:
            tags.append(category_map[analysis["category"]])
        
        # 紧急标签
        if analysis["urgency_level"] == "high":
            tags.append("紧急")
        
        # 意向标签
        if analysis["purchase_intent"] == "high":
            tags.append("高意向")
        
        # 情绪标签
        if analysis["sentiment"] == "negative":
            tags.append("需关注")
        
        return tags
    
    def generate_reply_suggestions(self, email_content: dict, analysis: dict = None) -> List[dict]:
        """
        生成智能回复建议
        
        Returns:
            [
                {
                    "title": "专业报价",
                    "description": "详细报价单，包含价格和交期",
                    "content": "邮件正文..."
                },
                ...
            ]
        """
        if not analysis:
            analysis = self.analyze_email(email_content)
        
        suggestions = []
        category = analysis.get("category", "general")
        
        # 根据不同类型生成不同的回复建议
        if category == "inquiry":
            suggestions = self._inquiry_replies()
        elif category == "order":
            suggestions = self._order_replies()
        elif category == "sample":
            suggestions = self._sample_replies()
        elif category == "complaint":
            suggestions = self._complaint_replies()
        else:
            suggestions = self._general_replies()
        
        return suggestions[:3]  # 返回前3个建议
    
    def _inquiry_replies(self) -> List[dict]:
        """询价邮件回复建议"""
        return [
            {
                "title": "专业报价",
                "description": "详细报价，含价格阶梯和交期",
                "content": """Dear [Customer],\n\nThank you for your inquiry about our men's underwear products.\n\nBased on your requirements, here is our quotation:\n\n• Product: Men's Cotton Boxer Briefs\n• MOQ: 500 pcs per design\n• Price: $3.50-$5.80/pc (depending on quantity)\n• Lead time: 25-30 days after sample approval\n• Payment: 30% deposit, 70% before shipment\n\nWe can provide free samples for your evaluation. Would you like us to send you our latest catalog?\n\nBest regards,\n[Your Name]"""
            },
            {
                "title": "快速响应",
                "description": "简短确认，询问详细需求",
                "content": """Hi [Customer],\n\nThank you for reaching out! We'd be happy to provide a quotation.\n\nTo prepare an accurate quote, could you please share:\n• Target quantity per order\n• Preferred materials/styles\n• Target delivery date\n• Your location for shipping calculation\n\nI'll send you a detailed proposal within 24 hours.\n\nBest,\n[Your Name]"""
            },
            {
                "title": "增值服务",
                "description": "突出优势，提供额外价值",
                "content": """Dear [Customer],\n\nGreat to hear from you! Our factory specializes in premium men's underwear with 15+ years of experience.\n\n✓ Low MOQ (500pcs)\n✓ OEM/ODM service\n✓ Free design support\n✓ Quality guarantee\n✓ Fast sampling (3-5 days)\n\nI've attached our product catalog and can provide a custom quotation based on your specific needs.\n\nShall we schedule a quick call this week to discuss your project?\n\nBest regards,\n[Your Name]"""
            }
        ]
    
    def _order_replies(self) -> List[dict]:
        """订单确认回复"""
        return [
            {
                "title": "订单确认",
                "description": "确认订单详情",
                "content": """Dear [Customer],\n\nThank you for your order! We're excited to work with you.\n\nOrder confirmed:\n• Order No.: [ORDER_NO]\n• Quantity: [QTY] pcs\n• Total Amount: $[AMOUNT]\n• Deposit: $[DEPOSIT] (30%)\n• Production time: [DAYS] days\n\nPlease find the attached Proforma Invoice. Once we receive the deposit, we'll start production immediately.\n\nLooking forward to a successful cooperation!\n\nBest regards,\n[Your Name]"""
            }
        ]
    
    def _sample_replies(self) -> List[dict]:
        """样品请求回复"""
        return [
            {
                "title": "样品确认",
                "description": "确认寄送样品",
                "content": """Dear [Customer],\n\nThank you for your interest in our samples!\n\nWe offer FREE samples, you only need to cover the shipping cost (approximately $[AMOUNT] by DHL/FedEx).\n\nPlease provide:\n• Full shipping address\n• Contact phone number\n• Preferred styles/sizes\n\nWe'll send the samples within 2-3 business days and provide tracking information.\n\nBest regards,\n[Your Name]"""
            }
        ]
    
    def _complaint_replies(self) -> List[dict]:
        """投诉处理回复"""
        return [
            {
                "title": "诚挚道歉",
                "description": "表达歉意，提供解决方案",
                "content": """Dear [Customer],\n\nThank you for bringing this to our attention. We sincerely apologize for the inconvenience.\n\nWe take quality very seriously and are investigating this issue immediately. Here's how we'll resolve it:\n\n1. Send replacement products at no charge\n2. Provide compensation/discount on next order\n3. Improve our QC process to prevent future issues\n\nCould we schedule a call today to discuss the best solution for you?\n\nOnce again, our apologies for this situation.\n\nBest regards,\n[Your Name]"""
            }
        ]
    
    def _general_replies(self) -> List[dict]:
        """通用回复"""
        return [
            {
                "title": "专业回复",
                "description": "礼貌确认收到",
                "content": """Dear [Customer],\n\nThank you for your email. We've received your message and are reviewing the details.\n\nWe'll get back to you within 24 hours with a comprehensive response.\n\nIf you need immediate assistance, please feel free to call us at [PHONE].\n\nBest regards,\n[Your Name]"""
            }
        ]
    
    def polish_email(self, content: str, tone: str = "professional") -> str:
        """
        润色邮件内容
        
        Args:
            content: 原始邮件内容
            tone: 语气 (professional/friendly/urgent)
            
        Returns:
            润色后的邮件内容
        """
        # 简化版本 - 实际应该调用OpenAI API
        polished = content.strip()
        
        # 添加适当的开头
        if not polished.startswith(("Hi", "Hello", "Dear")):
            polished = "Dear Customer,\n\n" + polished
        
        # 添加结尾
        if not polished.endswith(("regards", "Regards", "Best")):
            polished += "\n\nBest regards,\nYour Name"
        
        return polished
    
    def translate_email(self, content: str, target_lang: str = "en") -> str:
        """
        翻译邮件
        
        Args:
            content: 原文
            target_lang: 目标语言 (en/zh/es/fr)
            
        Returns:
            翻译后的内容
        """
        try:
            # 🔥 语言映射
            lang_map = {
                'zh': '简体中文',
                'en': 'English',
                'es': 'Spanish',
                'fr': 'French',
                'de': 'German',
                'ja': 'Japanese',
                'ko': 'Korean'
            }
            
            target_language = lang_map.get(target_lang, target_lang)
            
            # 🔥 使用 OpenAI API 翻译
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": f"你是一个专业的翻译助手。请将提供的文本翻译成{target_language}。\n\n翻译要求：\n1. 保持原文的格式（段落、换行等）\n2. 保持专业的语气\n3. 如果有HTML标签，请保留HTML标签，只翻译内容\n4. 直接返回翻译结果，不要添加额外说明"
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            translated = response.choices[0].message.content
            return translated.strip()
            
        except Exception as e:
            print(f"❌ 翻译失败: {str(e)}")
            # 🔥 如果 API 调用失败，返回简单提示
            return f"[翻译服务暂时不可用]\n{content}"
    
    def extract_action_items(self, email_content: dict) -> List[dict]:
        """
        提取待办事项
        
        Returns:
            [
                {"task": "发送样品", "due_date": "2026-01-20"},
                {"task": "准备报价单", "due_date": None}
            ]
        """
        body = email_content.get("body", "").lower()
        actions = []
        
        if "sample" in body or "样品" in body:
            actions.append({"task": "发送样品", "due_date": None})
        
        if "quote" in body or "price" in body or "报价" in body:
            actions.append({"task": "准备报价单", "due_date": None})
        
        if "call" in body or "meeting" in body or "电话" in body:
            actions.append({"task": "安排通话/会议", "due_date": None})
        
        return actions
