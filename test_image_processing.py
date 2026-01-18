"""测试邮件图片处理功能"""
import re

# 模拟HTML内容
test_html = """
<html>
<body>
    <h1>测试邮件</h1>
    <p>这是一封测试邮件，包含图片：</p>
    
    <!-- 内嵌图片（CID引用） -->
    <img src="cid:image001.jpg@01DA9999.12345678" alt="内嵌图片1">
    <img src='cid:logo.png@01DA9999.ABCDEF' alt="内嵌图片2">
    
    <!-- 外部图片 -->
    <img src="https://example.com/image1.jpg" alt="外部图片1">
    <img src="http://example.com/image2.png" alt="外部图片2">
    
    <!-- Data URL（不应处理） -->
    <img src="data:image/png;base64,iVBORw0KG..." alt="Base64图片">
    
    <p>邮件结束</p>
</body>
</html>
"""

# 测试内嵌图片映射
inline_images = {
    'image001.jpg@01DA9999.12345678': '1234567890_abc123.jpg',
    'logo.png@01DA9999.ABCDEF': '1234567891_def456.png'
}

# 测试 CID 替换 - 使用简单的字符串替换
processed_html = test_html

for cid, stored_filename in inline_images.items():
    old_src1 = f'cid:{cid}'
    old_src2 = f'cid:{cid.strip("<>")}'  # 也尝试清理后的
    new_src = f'/api/email_history/123/images/{stored_filename}'
    
    processed_html = processed_html.replace(old_src1, new_src)
    processed_html = processed_html.replace(old_src2, new_src)

print("=" * 60)
print("测试邮件图片处理")
print("=" * 60)
print("\n原始HTML:")
print(test_html)
print("\n" + "=" * 60)
print("\n处理后的HTML:")
print(processed_html)
print("\n" + "=" * 60)

# 验证替换结果
if '/api/email_history/123/images/1234567890_abc123.jpg' in processed_html:
    print("\n✅ 内嵌图片1替换成功")
else:
    print("\n❌ 内嵌图片1替换失败")

if '/api/email_history/123/images/1234567891_def456.png' in processed_html:
    print("✅ 内嵌图片2替换成功")
else:
    print("❌ 内嵌图片2替换失败")

if 'https://example.com/image1.jpg' in processed_html:
    print("✅ 外部图片URL保留（待后续处理）")
else:
    print("❌ 外部图片URL丢失")

if 'data:image/png;base64' in processed_html:
    print("✅ Data URL保留")
else:
    print("❌ Data URL丢失")

print("\n" + "=" * 60)
print("测试完成！")
