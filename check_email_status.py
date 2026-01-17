import sqlite3

conn = sqlite3.connect('data/customers.db')
cursor = conn.cursor()

print("=" * 60)
print("检查邮件删除状态")
print("=" * 60)

cursor.execute('''
    SELECT id, subject, is_deleted, deleted_at 
    FROM email_history 
    ORDER BY id DESC 
    LIMIT 10
''')

print("\n最近的10封邮件:")
print("-" * 60)
for row in cursor.fetchall():
    email_id, subject, is_deleted, deleted_at = row
    status = "已删除" if is_deleted else "正常"
    print(f"ID: {email_id}")
    print(f"主题: {subject or '(无主题)'}")
    print(f"状态: {status}")
    print(f"删除时间: {deleted_at or '未删除'}")
    print("-" * 60)

# 统计已删除的邮件数量
cursor.execute('SELECT COUNT(*) FROM email_history WHERE is_deleted = 1')
deleted_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM email_history WHERE is_deleted = 0')
normal_count = cursor.fetchone()[0]

print(f"\n统计:")
print(f"正常邮件: {normal_count} 封")
print(f"回收站邮件: {deleted_count} 封")
print(f"总计: {normal_count + deleted_count} 封")

conn.close()
