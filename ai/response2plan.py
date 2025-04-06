from datetime import datetime, date

class Plan:
    def __init__(self, thing, description, day, start_date, end_date):
        self.thing = thing
        self.description = description
        self.day = day
        self.start_date = start_date
        self.end_date = end_date

def parse_plans(input_text):
    """
    将输入的计划文本解析为 Plan 模型实例并保存到数据库
    """
    plans = []
    lines = input_text.strip().split("\n")
    for line in lines:
        if line.startswith("p"):
            # 提取用户 ID 和周几
            user_id, content = line.split(":", 1)
            day = int(user_id[1])  # 提取 p1, p2 中的数字作为周几
            parts = [part.strip() for part in content.split(";")]
            # 过滤掉空字符串
            parts = [part for part in parts if part]
            if len(parts) >= 4:
                # 提取计划内容
                start_time = datetime.strptime(parts[0].strip(), "%H:%M").time()
                end_time = datetime.strptime(parts[1].strip(), "%H:%M").time()
                thing = parts[2].strip()
                description = parts[3].strip()

                # 创建并保存 Plan 实例
                plan = Plan(
                    thing=thing,
                    description=description,
                    day=day,
                    start_date=start_time,  # 假设计划从今天开始
                    end_date=end_time,    # 假设计划今天结束
                )
                plans.append(plan)
    return plans