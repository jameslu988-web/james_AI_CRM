import re


class EmailFinder:
    """邮箱查找与验证"""
    
    def __init__(self):
        self.common_patterns = [
            '{first}.{last}@{domain}',
            '{first}@{domain}',
            '{first}{last}@{domain}',
            '{f}{last}@{domain}',
            'info@{domain}',
            'contact@{domain}',
            'sales@{domain}',
        ]
    
    def extract_domain(self, url):
        """从URL提取域名"""
        import re
        match = re.search(r'(?:https?://)?(?:www\.)?([^/]+)', url)
        if match:
            return match.group(1)
        return None
    
    def find_email(self, domain, first_name=None, last_name=None):
        """
        根据域名和姓名查找邮箱
        参数:
            domain: 公司域名
            first_name: 名
            last_name: 姓
        返回:
            可能的邮箱列表
        """
        if not domain:
            return []
        
        emails = []
        
        if first_name and last_name:
            for pattern in self.common_patterns[:4]:
                email = pattern.format(
                    first=first_name.lower(),
                    last=last_name.lower(),
                    f=first_name[0].lower() if first_name else '',
                    domain=domain
                )
                emails.append(email)
        
        # 通用邮箱
        for pattern in self.common_patterns[4:]:
            email = pattern.format(domain=domain)
            emails.append(email)
        
        return emails
    
    def verify_email_format(self, email):
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def get_company_emails(self, domain):
        """获取公司常用邮箱"""
        return self.find_email(domain)
