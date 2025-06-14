import os
from django.http import JsonResponse
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

client = OpenAI(
    base_url='https://api.nuwaapi.com/v1',
    api_key='sk-iLxm9KdqaGG3uj1YOMg8ArlBvusu9USU7r5JdxnwEcWCQIC5'  # 替换为你的 Nuwa API Key
)