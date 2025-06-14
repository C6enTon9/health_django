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
from plan.services import create_or_update_plans, get_user_plans, delete_plan
from core.types import ServiceResult
from .services import client

# 将所有 AI 可用工具放入一个字典
AVAILABLE_TOOLS = {
    "update_user_info": update_user_info,
    "get_user_info": get_user_info,
    "create_or_update_plans": create_or_update_plans,
    "get_user_plans": get_user_plans,
    "delete_plan": delete_plan,
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
            "description": "为用户创建或更新一个周常计划，可以是运动或饮食。必须提供描述。",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "计划标题。运动是'跑步'，饮食是'早餐'等。"},
                    "description": {"type": "string", "description": "详细描述。饮食必须包含食物，运动可描述地点强度。"},
                    "day_of_week": {"type": "integer", "description": "星期几(1-7)。"},
                    "start_time": {"type": "string", "description": "开始时间 'HH:MM'。"},
                    "end_time": {"type": "string", "description": "结束时间 'HH:MM'。"},
                    "id": {"type": "integer", "description": "仅在更新时提供ID。"},
                },
                "required": ["title", "day_of_week", "start_time", "end_time", "description"]
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
    }
]

def rebuild_and_validate_messages(history: List[Dict[str, Any]], new_user_message: str) -> Optional[List[ChatCompletionMessageParam]]:
    """
    接收前端传来的历史记录和新消息，将其重构为 OpenAI API 能接受的干净格式。
    """
    system_prompt = """你是一个能干、简洁的个人健康助理。

        **你的核心任务是调用工具来管理用户的健康计划，并用自然语言进行回复。**

        **【行为准则】**

        **1. 关于工具调用:**
           - 你可以创建、更新、查询、删除用户的运动和饮食计划。
           - **创建/更新计划时 (`create_or_update_plans`)，必须提供 `description` 字段。**
           - **删除计划时 (`delete_plan`)，必须先通过 `get_user_plans` 获取 `plan_id` 并与用户确认。**

        **2. 关于回复用户 (最重要！):**
           - 当你调用**创建、更新或删除**计划的工具 (`create_or_update_plans`, `delete_plan`) 并从工具那里收到了一个表示**成功**的 JSON 结果 (例如 `{"code": 200, ...}`) 后：
             - **你绝对不准将这个 JSON 结果的任何部分（如 'code', 'data', 'id'）直接展示或复述给用户。**
             - 你**必须**根据操作的类型，生成一句**全新的、自然的、总结性的确认话语**。

           - **回复范例 (必须严格遵守):**
             - **创建成功后**: 不要说 "已创建，ID是103"，而是说 "好的，我已经为您安排好了周一的晨跑计划。" 或者 "没问题，您的早餐计划已经添加。"
             - **更新成功后**: 不要说 "更新成功，updated: 1"，而是说 "好的，我已经将您的计划更新为晚上8点健身。"
             - **删除成功后**: 不要说 "已删除，deleted: 1"，而是说 "好的，我已经帮您取消了那个计划。"

           - **只有在调用查询工具 (`get_user_plans`) 时**，你才需要将查询到的计划内容（标题、时间等）以清晰的列表形式展示给用户，以便他们进行后续操作。

        请严格遵循以上所有规则，尤其是关于**如何回复用户**的规则。"""

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