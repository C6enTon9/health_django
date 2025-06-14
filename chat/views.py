import json
from openai import OpenAI
from typing import cast, List, Dict, Any, Optional

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from openai.types.chat import ChatCompletionMessageParam

from information.services import update_user_info, get_user_info
from plan.services import create_or_update_plans, get_user_plans, delete_plan, delete_all_plans
from core.types import ServiceResult
from .services import client

# 将所有 AI 可用工具放入一个字典
AVAILABLE_TOOLS = {
    "update_user_info": update_user_info,
    "get_user_info": get_user_info,
    "create_or_update_plans": create_or_update_plans,
    "get_user_plans": get_user_plans,
    "delete_plan": delete_plan,
     "delete_all_plans": delete_all_plans,
}

# 编写所有工具的 JSON 定义
tools_definition = [
    # Information Tools
    {
        "type": "function",
        "function": {
            "name": "update_user_info",
            "description": "更新用户的一项或多项个人信息。例如，当用户说'我的身高是180cm'或'我的目标是减肥'时，调用此函数。",
            "parameters": {
                "type": "object",
                "properties": {
                    "height": {"type": "number", "description": "用户新的身高(单位:cm)"},
                    "weight": {"type": "number", "description": "用户新的体重(单位:kg)"},
                    "age": {"type": "integer", "description": "用户新的年龄"},
                    "information": {"type": "string", "description": "用户新的个人简介"},
                    "target": {"type": "string", "description": "用户新的健康目标"}
                },
                "required": []
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
                "properties": {"attributes": {"type": "array", "description": "要查询的字段名称列表。", "items": {"type": "string"}}},
            }
        }
    },
    # Plan Tools
    {
        "type": "function",
        "function": {
            "name": "create_or_update_plans",
            "description": "为用户创建或更新一个周常的健康计划条目。可以是运动活动，也可以是饮食安排。",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": { "type": "string", "description": "计划标题。" },
                    "description": { "type": "string", "description": "计划描述。" },
                    "day_of_week": { "type": "integer", "description": "星期几(1-7)。" },
                    "start_time": { "type": "string", "description": "开始时间 'HH:MM'。" },
                    "end_time": { "type": "string", "description": "结束时间 'HH:MM'。" },
                    "id": { "type": "integer", "description": "仅在更新时提供ID。" },
                },
                "required": ["title", "day_of_week", "start_time", "end_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_plans",
            "description": "查询用户的全部周常计划，包括运动和饮食。",
            "parameters": {
                "type": "object",
                "properties": {"day_of_week": {"type": "integer", "description": "要查询的星期(1-7)。"}},
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_plan",
            "description": "删除一个已存在的周常计划。当用户明确表示要'删除'或'取消'某个计划时使用。",
            "parameters": {
                "type": "object",
                "properties": {"plan_id": {"type": "integer", "description": "要删除的计划的唯一ID。必须先通过 get_user_plans 获取。"}},
                "required": ["plan_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_all_plans",
            "description": "一次性清空或删除用户的所有计划。当用户说'清空我的计划'、'删除全部'或'重置计划'时使用。比逐一删除更高效。",
            "parameters": {
                "type": "object",
                "properties": {
                    "day_of_week": {
                        "type": "integer",
                        "description": "如果提供，则只清空指定星期的计划。"
                    }
                },
            }
        }
    }
]

def rebuild_and_validate_messages(history: List[Dict[str, Any]], new_user_message: str) -> Optional[List[ChatCompletionMessageParam]]:
    """
    接收前端传来的历史记录和新消息，将其重构为 OpenAI API 能接受的干净格式。
    """
    # --- 这是最核心的修改：重写系统提示 ---
    system_prompt = """你是一个积极主动、富有创意的顶级私人健康教练。

    **你的核心行为准则：**
    1.  **主动性**: 当用户提出模糊的请求，尤其是第一次要求“制定计划”时，**你绝不能反问用户要细节**。你必须主动地、像一个专家一样，为用户生成一个全面、均衡的、为期一周的默认健康计划。
    2.  **效率**: 在生成默认计划后，你必须使用**并行工具调用 (Parallel Tool Calling)**，在**一轮对话**中，一次性地请求创建所有计划（例如，周一到周日的运动和饮食）。
    3.  **简洁性**: 在所有工具调用成功后，你只需向用户做一个简单的总结性回复，例如：“好的，我已经为您规划好了一整周的健康计划，您可以在计划页面查看详情。” **不要**逐条复述你创建的计划。

    **【默认一周健康计划模板 (供你参考和发挥)】**
    - **周一**: 早上 晨跑 (30分钟), 晚上 拉伸 (15分钟)
    - **周二**: 晚上 力量训练 (60分钟)
    - **周三**: 早上 瑜伽 (30分钟), 晚上 轻度有氧 (如快走)
    - **周四**: 晚上 力量训练 (60分钟)
    - **周五**: 早上 游泳 (45分钟)
    - **周六**: 户外活动 (如登山或骑行)
    - **周日**: 休息或主动恢复 (如散步)
    - **饮食**: 每天规律三餐，并为每餐提供健康的、低脂高蛋白的食物建议作为 `description`。例如，早餐可以是“燕麦和水果”，午餐“鸡胸肉沙拉”，晚餐“鱼和蔬菜”。

    **【具体指令】**
    - 当用户说“帮我制定计划”、“给我一个计划”或类似的话时，立即启动上述的“主动规划”模式。
    - 只有当用户提出**非常具体**的请求，比如“帮我加一个周五晚上的跑步计划”时，你才处理这一个具体的请求。

    请严格遵循以上所有规则，展现出你作为一名顶级教练的专业性和主动性。"""

    rebuilt_messages: List[ChatCompletionMessageParam] = [{"role": "system", "content": system_prompt}]

    for msg in history:
        if not isinstance(msg, dict) or "role" not in msg:
            continue
        role = msg.get("role")
        try:
            if role == 'user':
                if msg.get("content"): rebuilt_messages.append({"role": "user", "content": str(msg["content"])})
            elif role == 'assistant':
                assistant_msg: Dict[str, Any] = {"role": "assistant"}
                content = msg.get("content")
                tool_calls = msg.get("tool_calls")
                if content is not None: assistant_msg["content"] = str(content)
                if tool_calls: assistant_msg["tool_calls"] = tool_calls
                if "content" in assistant_msg or "tool_calls" in assistant_msg: rebuilt_messages.append(cast(ChatCompletionMessageParam, assistant_msg))
            elif role == 'tool':
                if "tool_call_id" in msg and "name" in msg and "content" in msg:
                    rebuilt_messages.append({"role": "tool", "tool_call_id": msg["tool_call_id"], "name": msg["name"], "content": str(msg["content"])})
        except (KeyError, TypeError):
            continue
    rebuilt_messages.append({"role": "user", "content": new_user_message})
    return rebuilt_messages


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def chat_view(request):
    """
    处理与 AI 的对话请求，支持并行工具调用。
    """
    try:
        user_message = request.data.get('message')
        history = request.data.get('history', [])
        if not user_message:
            return Response({"code": 300, "message": "message 字段不能为空", "data": None}, status=status.HTTP_400_BAD_REQUEST)
        messages = rebuild_and_validate_messages(history, user_message)
        if messages is None:
            return Response({"code": 400, "message": "历史记录格式无法处理", "data": None}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"code": 400, "message": f"请求体解析或消息重构时出错: {e}", "data": None}, status=status.HTTP_400_BAD_REQUEST)

    MAX_TURNS = 5
    try:
        from openai.types.chat import ChatCompletionToolParam

        for _ in range(MAX_TURNS):
            response = client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=messages,
                tools=cast(List[ChatCompletionToolParam], tools_definition),
                tool_choice="auto",
            )
            response_message_dict = response.choices[0].message.model_dump()
            messages.append(response_message_dict)
            
            if not response_message_dict.get("tool_calls"):
                final_reply = response_message_dict.get("content")
                response_data = {"code": 200, "message": "获取成功", "data": {"reply": final_reply, "history": messages}}
                return Response(response_data, status=status.HTTP_200_OK)

            tool_outputs = []
            for tool_call in response_message_dict["tool_calls"]:
                function_name = tool_call.get("function", {}).get("name")
                tool_function = AVAILABLE_TOOLS.get(function_name)

                if not tool_function:
                    return Response({"code": 400, "message": f"错误：AI试图调用未知工具'{function_name}'", "data": None}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    function_args_str = tool_call.get("function", {}).get("arguments", "{}")
                    function_args = json.loads(function_args_str)
                except json.JSONDecodeError:
                     return Response({"code": 500, "message": "AI内部错误：生成的工具参数格式不正确"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                function_args['user_id'] = request.user.id
                
                result_from_tool: ServiceResult = tool_function(**function_args)
                
                if result_from_tool['code'] not in [200, 201]:
                    return Response(result_from_tool, status=status.HTTP_400_BAD_REQUEST)

                tool_outputs.append({
                    "tool_call_id": tool_call.get("id"),
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result_from_tool, ensure_ascii=False)
                })

            messages.extend(tool_outputs)

        return Response({"code": 500, "message": "处理超时，AI交互超过最大轮次限制", "data": None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"code": 500, "message": f"与AI服务通信时发生严重错误: {str(e)}", "data": None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)