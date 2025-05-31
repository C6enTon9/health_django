from deepseek import chat
from response2plan import parse_plans

def main():
    # 模拟用户输入
    user_id = "12345"
    user_information = "年龄: 30, 性别: 男, 健康状况: 良好, 目标: 减脂。"

    # 获取 AI 响应
    print("🔍 正在获取健康计划...\n")
    try:
        response_content = chat(user_id, user_information)
    except Exception as e:
        print(f"❌ 调用 chat 失败: {e}")
        return

    print("✅ 原始响应内容:")
    print(response_content)
    
    # 解析计划
    print("\n🧩 正在解析计划...\n")
    try:
        plans = parse_plans(response_content)
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return

    print(f"✅ 共解析出 {len(plans)} 个计划项目\n")

    # 打印每个计划的详细信息
    for i, plan in enumerate(plans, 1):
        print(f"📅 计划 {i}:")
        print(f"  - 周 {plan.day}")
        print(f"  - 时间：{plan.start_time.strftime('%H:%M')} ~ {plan.end_time.strftime('%H:%M')}")
        print(f"  - 项目：{plan.thing}")
        print(f"  - 描述：{plan.description}")
        print("-" * 40)

if __name__ == "__main__":
    main()
