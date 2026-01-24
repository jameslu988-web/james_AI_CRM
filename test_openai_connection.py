import asyncio
from openai import AsyncOpenAI

async def test():
    client = AsyncOpenAI(
        api_key='sk-5dn0RF7nn31mpHNjEfC5Ca1579F447418aE48e7b0d8b18F7',
        base_url='https://aihubmix.com/v1'
    )
    
    try:
        print("正在测试OpenAI连接...")
        resp = await client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role':'user','content':'Say hello'}],
            timeout=10
        )
        print(f"✅ 连接成功！")
        print(f"响应: {resp.choices[0].message.content}")
    except Exception as e:
        print(f"❌ 连接失败: {type(e).__name__}: {str(e)}")

asyncio.run(test())
