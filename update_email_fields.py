"""
更新邮件历史中缺失的from_email和to_email字段
尝试从现有客户数据中推断发件人邮箱
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("data/customers.db")

def update_email_fields():
    """更新邮件历史中缺失的邮箱字段"""
    if not DB_PATH.exists():
        print("❌ 数据库文件不存在")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 查询缺失from_email的邮件记录
        cursor.execute("""
            SELECT id, customer_id, direction 
            FROM email_history 
            WHERE from_email IS NULL OR from_email = ''
        """)
        emails = cursor.fetchall()
        
        if not emails:
            print("✅ 所有邮件记录都有完整的邮箱信息")
            return True
        
        print(f"📊 发现 {len(emails)} 条邮件记录缺失发件人信息")
        print("\n开始更新...")
        
        updated_count = 0
        
        for email_id, customer_id, direction in emails:
            if customer_id:
                # 从客户表获取邮箱
                cursor.execute("SELECT email FROM customers WHERE id = ?", (customer_id,))
                result = cursor.fetchone()
                
                if result and result[0]:
                    customer_email = result[0]
                    
                    # 根据方向设置from_email和to_email
                    if direction == 'inbound':
                        # 入站邮件：客户发给我们
                        from_email = customer_email
                        to_email = None  # 收件人是我们的邮箱，可以后续手动填写
                    else:
                        # 出站邮件：我们发给客户
                        from_email = None  # 发件人是我们的邮箱，可以后续手动填写
                        to_email = customer_email
                    
                    cursor.execute("""
                        UPDATE email_history 
                        SET from_email = ?, to_email = ?
                        WHERE id = ?
                    """, (from_email, to_email, email_id))
                    
                    updated_count += 1
        
        conn.commit()
        
        print(f"\n✅ 成功更新 {updated_count} 条邮件记录")
        
        if updated_count < len(emails):
            remaining = len(emails) - updated_count
            print(f"\nℹ️  还有 {remaining} 条邮件记录无法自动更新（没有关联客户或客户无邮箱）")
            print("建议：删除这些记录并重新同步邮件")
        
        return True
        
    except Exception as e:
        print(f"❌ 更新失败: {str(e)}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("更新邮件历史中缺失的邮箱字段")
    print("=" * 60)
    print()
    
    update_email_fields()
    
    print("\n📝 提示：")
    print("- 已根据关联的客户信息自动填充邮箱字段")
    print("- 如果还有记录显示为空，建议删除并重新同步邮件")
    print("- 新同步的邮件会包含完整的发件人和收件人信息")
