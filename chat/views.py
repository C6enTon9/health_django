# chat/views.py

import json
import os
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from openai import OpenAI
from typing import cast, List, Dict, Any

# --- 1. 使用正确的绝对导入 ---
from information.services import update_user_info, get_user_info
from plan.services import create_or_update_plans, get_user_plans
from core.types import ServiceResult

from .services import client

# --- 3. 将所有 AI 可用工具放入一个字典，方便查找 ---
AVAILABLE_TOOLS = {
    "update_user_info": update_user_info,
    "get_user_info": get_user_info,
    "create_or_update_plans": create_or_update_plans,
    "get_user_plans": get_user_plans,
}

# --- 4. 编写所有工具的 JSON 定义，告诉 AI 如何使用它们 ---
# (这部分无需修改，保持原样)
tools_definition = [
    # Information Tools
    {
        "type": "function",
        "function": {
            "name": "update_user_info",
            "description": "更新用户的一项或多项个人信息，如身高、体重、年龄、个人简介或目标。",
            "parameters": {
                "type": "object",
                "properties": {"updates": {"type": "object", "description": "一个包含要更新的字段和新值的字典。例如：{'weight': 75.5}"}},
                "required": ["updates"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_info",
            "description": "查询用户的一项或多项个人信息。如果不指定，则返回全部信息。",
            "parameters": {
                "type": "object",
                "properties": {"attributes": {"type": "array", "description": "要查询的字段名称列表。例如：['weight', 'height']", "items": {"type": "string"}}},
            }
        }
    },
    # Plan Tools
    {
        "type": "function",
        "function": {
            "name": "create_or_update_plans",
            "description": "为用户创建或更新一个或多个周常计划。必须在获取了用户的个人信息和现有计划后才能调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "plans_data": {
                        "type": "array", "description": "一个计划列表，每个计划都是一个包含详细信息的字典。",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "description": "计划ID，仅在更新时提供。"},
                                "title": {"type": "string", "description": "计划标题，如'晨跑'。"},
                                "day_of_week": {"type": "integer", "description": "星期几(1-7)。"},
                                "start_time": {"type": "string", "description": "开始时间，格式'HH:MM'。"},
                                "end_time": {"type": "string", "description": "结束时间，格式'HH:MM'。"}
                            }, "required": ["title", "day_of_week", "start_time", "end_time"]
                        }
                    }
                }, "required": ["plans_data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_plans",
            "description": "查询用户的周常计划。当用户想知道'我有什么计划'时使用。",
            "parameters": {
                "type": "object",
                "properties": {"day_of_week": {"type": "integer", "description": "要查询的星期(1-7)。如果省略，则查询所有计划。"}},
            }
        }
    }
]

@csrf_exempt
# @login_required # 在实际生产中，请务必开启登录验证！
@require_POST
def chat_view(request):
    """
    处理与 AI 的对话请求。
    此视图现在支持多步工具调用，允许 AI 在一个任务中按顺序调用多个函数。
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message')
        # 新增：接收前端传递的完整对话历史
        history = data.get('history', [])
        
        if not user_message:
            return JsonResponse({"code": 300, "message": "message 字段不能为空", "data": None}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"code": 300, "message": "无效的JSON格式", "data": None}, status=400)
    
    # --- 核心改动：将会话历史和新消息结合 ---
    messages = [
        {"role": "system", "content": """你是一个能干的个人健康助理，可以帮助用户管理个人信息和周常计划。

当用户要求生成或修改健康计划时，你必须严格遵循以下步骤：
1. **第一步**: 调用 `get_user_info` 获取用户的个人信息（如身高、体重、目标等）以获得全面的背景。
2. **第二步**: 调用 `get_user_plans` 获取用户现有的计划，以避免冲突或重复。
3. **第三步**: 在获得了上述所有信息后，结合用户的原始请求，生成一个经过深思熟虑的、完整的计划。
4. **第四步**: 调用 `create_or_update_plans` 来保存这个新计划。
5. **最后**: 在所有工具调用成功后，向用户总结你所做的操作，例如：“我已经根据您的信息为您制定了新的跑步计划。”

在其他情况下，请根据用户的指令，智能地选择并调用最合适的单个工具来完成任务。"""},
    ]
    # 将前端的历史记录加入，使其成为真正的多轮对话
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    # --- 核心改动：引入循环来处理多步工具调用 ---
    MAX_TURNS = 5  # 设置最大循环次数，防止无限循环
    
    try:
        from openai.types.chat import ChatCompletionToolParam

        for _ in range(MAX_TURNS):
            response = client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=messages,
                tools=cast(List[ChatCompletionToolParam], tools_definition),
                tool_choice="auto",
            )
            response_message = response.choices[0].message
            
            # 将AI的回复（可能是带工具调用的回复）也加入消息历史
            messages.append(response_message.model_dump())
            
            # --- 步骤 1: 检查AI是否决定调用工具 ---
            if not response_message.tool_calls:
                # 如果没有工具调用，说明AI认为任务已完成，直接返回其最终答复
                # 注意：在我们的流程中，如果成功创建计划，AI也应该给个总结性回复
                response_data = {"code": 200, "message": "获取成功", "data": {"reply": response_message.content, "history": messages}}
                return JsonResponse(response_data, status=200)

            # --- 步骤 2: 执行AI请求的工具 ---
            # 如果AI决定调用工具，我们在这里处理
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                tool_function = AVAILABLE_TOOLS.get(function_name)

                if not tool_function:
                    error_message = f"错误：AI试图调用未知工具'{function_name}'"
                    return JsonResponse({"code": 400, "message": error_message, "data": None}, status=400)

                # 准备并执行函数
                function_args = json.loads(tool_call.function.arguments)
                # !! 确保 user_id 在每次调用时都传递进去 !!
                # user_id = request.user.id if request.user.is_authenticated else 1 # 临时用1做测试
                function_args['user_id'] = 1

                result_from_tool: ServiceResult = tool_function(**function_args)
                
                # --- 重要：检查工具执行结果 ---
                # 如果任何一个工具调用失败，应立即中止并返回错误
                if result_from_tool['code'] != 200:
                    error_detail = result_from_tool.get('message', '工具执行失败')
                    response_data = {"code": 400, "message": f"工具 '{function_name}' 执行失败: {error_detail}", "data": result_from_tool}
                    return JsonResponse(response_data, status=400)

                # --- 步骤 3: 将工具执行结果追加到消息历史中 ---
                # 这是让AI知道上一步结果的关键
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result_from_tool) # 将整个 ServiceResult 作为内容返回给AI
                })

            # 循环继续，将带有工具结果的新 `messages` 列表再次发送给AI
            # AI会看到上一步的结果，然后决定下一步做什么（调用另一个工具或最终回复）

        # 如果循环了 MAX_TURNS 次还没结束，则强制退出并报错
        return JsonResponse({"code": 500, "message": "处理超时，AI交互超过最大轮次限制", "data": None}, status=500)

    except Exception as e:
        print(f"调用AI或工具时发生错误: {e}")
        return JsonResponse({"code": 500, "message": f"与AI服务通信时发生错误: {str(e)}", "data": None}, status=500)
