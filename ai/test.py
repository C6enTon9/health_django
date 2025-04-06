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

plans = parse_plans(response_content)
print("解析后的计划:")
print(f"共解析出 {len(plans)} 个计划项目")

# 打印每个计划的详细信息
for i, plan in enumerate(plans, 1):
    print(f"\n计划 {i}:")
    print(f"  周{plan.day}，{plan.start_date.strftime('%H:%M')} - {plan.end_date.strftime('%H:%M')}")
    print(f"  项目：{plan.thing}")
    print(f"  描述：{plan.description}")