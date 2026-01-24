===============================================
外贸CRM系统 - 登录问题快速修复指南
===============================================

当用户报告"无法登录"时，请按以下步骤操作：

【步骤1】运行快速修复脚本（推荐）
-------------------------------------------
cd d:\AI_Projects\Automation-systerm
python scripts\fix_login_issue.py

脚本会自动：
✓ 检查bcrypt版本（最常见问题）
✓ 测试bcrypt功能
✓ 重置admin密码为admin123
✓ 检查后端服务状态
✓ 测试登录功能

【步骤2】手动修复（如果脚本失败）
-------------------------------------------
1. 降级bcrypt版本
   pip install bcrypt==4.0.1

2. 重置admin密码
   python -c "
   import psycopg2
   from passlib.context import CryptContext
   pwd = CryptContext(schemes=['bcrypt'], deprecated='auto', bcrypt__rounds=12)
   h = pwd.hash('admin123')
   c = psycopg2.connect(host='localhost', port=5432, database='crm_system', user='postgres', password='postgres123')
   cur = c.cursor()
   cur.execute('UPDATE users SET hashed_password = %s WHERE username = \"admin\"', (h,))
   c.commit()
   c.close()
   print('密码已重置')
   "

3. 重启后端服务
   taskkill /F /IM python.exe
   python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8001

【登录凭据】
-------------------------------------------
用户名: admin
密码: admin123
地址: http://localhost:5173

【常见问题】
-------------------------------------------
Q: 为什么会出现登录问题？
A: 99%的情况是bcrypt版本升级到5.x导致与passlib不兼容

Q: 如何预防此问题？
A: requirements.txt中已锁定bcrypt==4.0.1，安装依赖时使用：
   pip install -r requirements.txt

Q: 其他用户能登录吗？
A: 可以，使用相同密码admin123，用户名为：
   - sales01
   - sales02
   - manager01

【诊断时间】
-------------------------------------------
使用快速修复脚本：2-3分钟
手动修复：5-10分钟

===============================================
最后更新: 2026-01-24
===============================================
