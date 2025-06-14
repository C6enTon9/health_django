from openai import OpenAI

client = OpenAI(
    base_url='https://api.nuwaapi.com/v1',
    api_key='sk-iLxm9KdqaGG3uj1YOMg8ArlBvusu9USU7r5JdxnwEcWCQIC5'  # 替换为你的 Nuwa API Key
)

completion = client.chat.completions.create(
    model="gpt-4o-2024-08-06",  # 建议先用文档里肯定存在的模型
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)
print(completion.choices[0].message.content)