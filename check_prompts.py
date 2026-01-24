from src.crm.database import get_session, PromptTemplate

db = get_session()

# 查询所有提示词模板
templates = db.query(PromptTemplate).all()
print(f"✅ 提示词模板数量: {len(templates)}\n")

# 查询默认回复模板
default_reply = db.query(PromptTemplate).filter_by(
    is_default=True, 
    template_type='reply', 
    is_active=True
).first()

print(f"📋 默认回复模板: {default_reply.name if default_reply else '❌ 无'}\n")

# 显示所有模板信息
for i, t in enumerate(templates, 1):
    print(f"{'='*60}")
    print(f"模板 {i}: {t.name}")
    print(f"类型: {t.template_type}")
    print(f"启用: {'✅' if t.is_active else '❌'}")
    print(f"默认: {'✅' if t.is_default else '❌'}")
    print(f"推荐模型: {t.recommended_model}")
    
    if t.system_prompt:
        print(f"\n系统提示词（前200字）:")
        print(t.system_prompt[:200] + "...")
    else:
        print(f"\n系统提示词: ❌ 无")
    
    if t.user_prompt_template:
        print(f"\n用户提示词模板（前200字）:")
        print(t.user_prompt_template[:200] + "...")
    print()

db.close()
