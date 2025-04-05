from datetime import datetime

class plan:
    def __init__(self, user_id, thing, description, day, start_date, end_date):
        self.user_id = user_id
        self.thing = thing
        self.description = description
        self.day = day
        self.start_date = start_date
        self.end_date = end_date

def parse_plans(input_text):
    plans = []
    lines = input_text.strip().split("\n")

    for line in lines:
        if line.startswith("p"):
            # 提取用户 ID 和周几
            user_id, content = line.split(":", 1)
            day = int(user_id[1])  # 提取 p1, p2 中的数字作为周几
            parts = content.split(";")
            if len(parts) == 4:
                # 提取计划内容
                start_time = datetime.strptime(parts[0].strip(), "%H:%M").time()
                end_time = datetime.strptime(parts[1].strip(), "%H:%M").time()
                thing = parts[2].strip()
                description = parts[3].strip()

                # 创建 Plan 实例
                plan = plan(
                    user_id=user_id,
                    thing=thing,
                    description=description,
                    day=day,
                    start_date=start_time,  # 修改为时间类型
                    end_date=end_time       # 修改为时间类型
                )
                plans.append(plan)

    return plans