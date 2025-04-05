from deepseek import chat
from response2plan import parse_plans
# 模拟用户输入
user_id = "12345"
user_information = "年龄: 30, 性别: 男, 健康状况: 良好, 目标: 减脂。"

# 调用 deepseek 的 chat 函数获取计划
response_content = chat(user_id, user_information)

# 打印原始响应内容
print("原始响应内容:")
print(response_content)

plan  = parse_plans(response_content)
print("解析后的计划:")
print(plan)