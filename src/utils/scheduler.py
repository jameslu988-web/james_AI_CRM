import schedule
import time
from datetime import datetime


class AutomationScheduler:
    """自动化任务调度器"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.is_running = False
    
    def setup_tasks(self):
        """设置定时任务"""
        # 每天早上9点：搜索新客户
        schedule.every().day.at("09:00").do(self.daily_prospecting)
        
        # 每天早上10点：发送邮件
        schedule.every().day.at("10:00").do(self.send_daily_emails)
        
        # 每2小时：检查邮件回复（占位）
        schedule.every(2).hours.do(self.check_email_replies)
        
        # 每天下午3点：订单状态检查
        schedule.every().day.at("15:00").do(self.check_orders)
        
        # 每周一：生成周报
        schedule.every().monday.at("09:00").do(self.generate_weekly_report)
        
        print("✅ 定时任务已设置")
    
    def daily_prospecting(self):
        """每日客户开发任务"""
        print(f"[{datetime.now()}] 开始搜索新客户...")
        from src.prospecting.google_scraper import GoogleScraper
        
        scraper = GoogleScraper()
        prospects = scraper.find_prospects(limit=50)
        print(f"✅ 找到 {len(prospects)} 个潜在客户")
        return prospects
    
    def send_daily_emails(self):
        """发送每日邮件"""
        print(f"[{datetime.now()}] 开始发送邮件...")
        from src.crm.database import Customer, EmailHistory
        from src.email_system.sender import EmailSender
        from src.email_system.ai_writer import AIEmailWriter
        
        # 获取需要跟进的客户
        today = datetime.now().date()
        customers_to_followup = self.db.query(Customer).filter(
            Customer.next_followup_date <= today,
            Customer.status.in_(['cold', 'contacted', 'replied'])
        ).limit(20).all()  # 每天最多20个
        
        sender = EmailSender()
        ai_writer = AIEmailWriter()
        sent_count = 0
        
        for customer in customers_to_followup:
            # 生成邮件
            prospect_data = {
                'company_name': customer.company_name,
                'contact_name': customer.contact_name,
                'email': customer.email,
                'industry': customer.industry or 'apparel'
            }
            email_body = ai_writer.generate_cold_email(prospect_data)
            
            # 发送邮件（占位）
            if sender.send_email(
                to_email=customer.email,
                subject="Premium Men's Underwear Manufacturer",
                body=email_body
            ):
                # 保存历史
                history = EmailHistory(
                    customer_id=customer.id,
                    direction='outbound',
                    subject="Premium Men's Underwear Manufacturer",
                    body=email_body,
                    sent_at=datetime.now(),
                    ai_generated=True
                )
                self.db.add(history)
                
                # 更新下次跟进日期
                from datetime import timedelta
                customer.next_followup_date = datetime.now().date() + timedelta(days=7)
                sent_count += 1
        
        self.db.commit()
        print(f"✅ 邮件发送任务完成，已发送 {sent_count} 封")
        return sent_count
    
    def check_email_replies(self):
        """检查邮件回复（占位）"""
        print(f"[{datetime.now()}] 检查邮件回复...")
        print("✅ 回复检查完成")
    
    def check_orders(self):
        """检查订单状态"""
        print(f"[{datetime.now()}] 检查订单状态...")
        from src.crm.database import Order
        from src.utils.notification import NotificationSystem
        
        # 查询延期订单
        today = datetime.now().date()
        delayed_orders = self.db.query(Order).filter(
            Order.estimated_completion_date < today,
            Order.status.in_(['production', 'confirmed', 'quotation'])
        ).all()
        
        if delayed_orders:
            notifier = NotificationSystem()
            for order in delayed_orders:
                customer = order.customer
                notifier.send_order_alert(
                    order.order_number,
                    customer.company_name if customer else 'Unknown',
                    'delayed'
                )
        
        print(f"✅ 订单检查完成，发现 {len(delayed_orders)} 个延期订单")
        return len(delayed_orders)
    
    def generate_weekly_report(self):
        """生成周报"""
        print(f"[{datetime.now()}] 生成周报...")
        from src.utils.reports import ReportGenerator
        from src.utils.notification import NotificationSystem
        
        reporter = ReportGenerator(self.db)
        report = reporter.generate_weekly_report()
        
        # 发送通知
        notifier = NotificationSystem()
        notifier.send_telegram(report)
        
        # 保存到文件
        import os
        os.makedirs('data/reports', exist_ok=True)
        report_file = f"data/reports/weekly_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 周报已生成并保存到 {report_file}")
        return report_file
    
    def run(self):
        """运行调度器"""
        self.is_running = True
        self.setup_tasks()
        
        print("🚀 自动化调度器已启动...")
        print("=" * 50)
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    def stop(self):
        """停止调度器"""
        self.is_running = False
        print("⏹️ 调度器已停止")
