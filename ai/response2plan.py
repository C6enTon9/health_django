from datetime import datetime, time
from typing import List,Optional

class Plan:
    def __init__(self, thing: str, description: str, day: int, start_time: time, end_time: time):
        self.thing = thing
        self.description = description
        self.day = day  # 第几天：1~7
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return f"Plan(day={self.day}, {self.start_time}-{self.end_time}, {self.thing})"

def parse_plans(input_text: Optional[str]) -> List[Plan]:
    """
    将输入的标准化计划文本解析为 Plan 实例列表。
    
    格式要求：
    每行形如：
    p1: 08:00; 10:00; 晨跑; 在公园跑步 5 公里;
    """
    plans = []
    if not input_text:
        print("无response")
        return []
    lines = input_text.strip().splitlines()

    for line in lines:
        line = line.strip()
        if not line or not line.startswith("p"):
            continue

        try:
            # 提取天数 p1, p2, ..., p7
            day_part, content = line.split(":", 1)
            day = int(day_part[1:])  # p1 -> 1

            parts = [part.strip() for part in content.split(";") if part.strip()]
            if len(parts) < 4:
                continue  # 无效格式

            start_time = datetime.strptime(parts[0], "%H:%M").time()
            end_time = datetime.strptime(parts[1], "%H:%M").time()
            thing = parts[2]
            description = parts[3]

            plan = Plan(
                thing=thing,
                description=description,
                day=day,
                start_time=start_time,
                end_time=end_time
            )
            plans.append(plan)
        except Exception as e:
            print(f"[Warning] 跳过无效行: {line}，错误: {e}")
            continue

    return plans
