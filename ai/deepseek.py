from openai import OpenAI
import datetime
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

# 从环境变量中读取配置
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

def build_prompt():
    today = datetime.date.today()
    intro = f"今天是{today}。"
    role_description = (
        "你是一个健康助手，下面我将给你用户的信息，你需要给出从今天开始一周的健康和饮食计划，"
        "要求有7天，每天有三个饮食规划和两个运动规划。要求标准化输出，其他额外内容不要。"
    )
    format_guide = (
        "请按照以下格式提供计划回复：每个任务以分号 (;) 分隔，任务的格式如下："
        "p<day>: <starttime>; <endtime>; <task_name>; <task_description>; "
        "- <day>: 任务的天数标识，例如 \"p1\" 表示第 1 天。"
        "- <starttime>: 任务的开始时间，例如 \"08:00\"。"
        "- <endtime>: 任务的结束时间，例如 \"10:00\"。"
        "- <task_name>: 任务的名称，例如 \"晨跑\"。"
        "- <task_description>: 任务的详细描述，例如 \"在公园跑步 5 公里\"。"
        "示例回复：p1: 08:00; 10:00; 晨跑; 在公园跑步 5 公里; p2: 14:00; 16:00; 阅读; 阅读一本书;"
    )
    return intro + role_description + format_guide

def chat(user_id: str, information: str, model="deepseek-chat", temperature=0.7):
    prompt = build_prompt()
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"User ID: {user_id}, Information: {information}"},
            ],
            stream=False,
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Error] Chat request failed: {e}"
