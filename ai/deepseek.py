# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI

client = OpenAI(api_key="sk-1cc155b06f5c4e55b9b06f7a5017328f", base_url="https://api.deepseek.com/v1")

import datetime
today = datetime.date.today()

prompt1 = f"今天是{today}。"
prompt2 =  "你是一个健康助手，下面我将给你用户的信息，你需要给出从今天开始一周的健康和饮食计划，要求有7天，每天有三个饮食规划和两个运动规划。要求标准化输出，其他额外内容不要。格式如下："
prompt3 = "请按照以下格式提供计划回复：每个任务以分号 (;) 分隔，任务的格式如下：p<day>: <starttime>; <endtime>; <task_name>; <task_description>; - <day>: 任务的天数标识，例如 \"p1\" 表示第 1 天。- <starttime>: 任务的开始时间，例如 \"08:00\"。- <endtime>: 任务的结束时间，例如 \"10:00\"。- <task_name>: 任务的名称，例如 \"晨跑\"。- <task_description>: 任务的详细描述，例如 \"在公园跑步 5 公里\"。示例回复：p1: 08:00; 10:00; 晨跑; 在公园跑步 5 公里; p2: 14:00; 16:00; 阅读; 阅读一本书;"
prompt = prompt1 + prompt2 + prompt3

def chat(user_id, information):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"User ID: {user_id}, Information: {information}"},
        ],
        stream=False,
        temperature=0.7
    )
    return response.choices[0].message.content