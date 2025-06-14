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
from plan.services import create_or_update_plans, get_user_plans, delete_plan, delete_all_plans,create_bulk_plans
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
    "create_bulk_plans": create_bulk_plans, 
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
    },
     {
        "type": "function",
        "function": {
            "name": "create_bulk_plans",
            "description": "最高效的计划创建工具。当需要一次性为用户创建多个（例如一整周的）计划时，必须使用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "plans_data": {
                        "type": "array",
                        "description": "一个包含多个计划对象的JSON数组。每个对象都应包含title, day_of_week, start_time, end_time, 和可选的description。",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "day_of_week": {"type": "integer"},
                                "start_time": {"type": "string", "pattern": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"},
                                "end_time": {"type": "string", "pattern": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"}
                            },
                            "required": ["title", "day_of_week", "start_time", "end_time"]
                        }
                    }
                },
                "required": ["plans_data"]
            }
        }
    }
]

def rebuild_and_validate_messages(history: List[Dict[str, Any]], new_user_message: str) -> Optional[List[ChatCompletionMessageParam]]:
    """
    接收前端传来的历史记录和新消息，将其重构为 OpenAI API 能接受的干净格式。
    """
    # --- 这是最核心的修改：重写系统提示 ---
    system_prompt = """你是一个积极主动、效率极高的顶级私人健康教练,能够主动提供健康计划和建议,包括饮食和运动,给出计划和建议的时候,要充分考虑用户的个人情况,在相关回复中体现出来你考虑的用户的情况,给出专业依据!!!

    **你的核心行为准则：**
    1.  **主动性**: 当用户提出模糊的请求，特别是第一次要求“制定计划”时，**你绝不能反问用户要细节**。你必须主动地、像一个专家一样，为用户生成一个全面、均衡的、为期一周的默认健康计划。
    2.  **效率至上 (最重要！)**:
        - 当你需要**创建多个计划**时（例如，在响应上述的模糊请求时），你**必须**使用 `create_bulk_plans` 工具。这个工具可以接收一个包含所有计划的数组，一次性完成任务。
        - **绝对不要**通过多次调用 `create_or_update_plans` 来创建多个计划，那样的效率太低。
        - 只有当用户明确要求**只修改或只添加一个**计划时，才使用 `create_or_update_plans`。
    3.  **批量删除**: 同样，当用户要求“清空计划”时，优先使用 `delete_all_plans` 工具。

    **【主动规划工作流】**
    当用户说“帮我制定一个计划”时，你的思考和行动步骤如下：
    1.  在脑海中构思一个完整的一周计划（参考下面的模板）。
    2.  将这个计划转换成一个 **JSON 数组**，数组中的每个元素都是一个符合 `create_bulk_plans` 工具 `items` 参数规范的对象。
    3.  调用 `create_bulk_plans` 工具，并将这个完整的 JSON 数组作为 `plans_data` 参数的值。
    4.  在工具调用成功后，给用户一个简洁的确认回复，例如：“好的，我已经为您规划好了一整周的健康计划，您可以在计划页面查看详情。”

    请严格遵循以上规则，始终选择最高效的工具来完成任务。"""

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
                model="gpt-4o-mini",
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