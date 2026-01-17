"""
清空邮件历史记录脚本
运行此脚本后，可以通过邮箱账户页面重新同步邮件，获取完整的发件人信息
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("data/customers.db")

def clear_email_history():
    """清空邮件历史记录"""
    if not DB_PATH.exists():
        print("❌ 数据库文件不存在")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 查询当前邮件数量
        cursor.execute("SELECT COUNT(*) FROM email_history")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("ℹ️  邮件历史记录为空，无需清空")
            return True
        
        print(f"📊 当前邮件历史记录数: {count}")
        
        # 确认操作
        confirm = input(f"\n⚠️  确认要删除所有 {count} 条邮件历史记录吗？(输入 yes 确认): ")
        
        if confirm.lower() != 'yes':
            print("❌ 操作已取消")
            return False
        
        # 删除所有邮件历史
        cursor.execute("DELETE FROM email_history")
        conn.commit()
        
        print(f"\n✅ 已成功删除 {count} 条邮件历史记录")
        print("\n📝 下一步操作：")
        print("1. 打开浏览器访问邮箱账户页面")
        print("2. 点击'同步邮件'按钮")
        print("3. 配置同步参数（建议设置日期范围）")
        print("4. 重新同步邮件，新数据将包含完整的发件人信息")
        
        return True
        
    except Exception as e:
        print(f"❌ 操作失败: {str(e)}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("清空邮件历史记录")
    print("=" * 60)
    print("\n注意：此操作将删除所有邮件历史记录！")
    print("删除后可通过邮箱账户页面重新同步，获取完整的邮箱信息\n")
    
    clear_email_history()
