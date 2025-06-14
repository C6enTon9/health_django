# plan/views.py

import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .services import create_or_update_plans, get_user_plans
from core.types import ServiceResult

@csrf_exempt

@require_http_methods(["POST"]) # 这个视图只接受 POST 请求
def manage_plans_view(request):
    """
    一个统一的视图，用于创建或更新一个或多个计划。
    前端需要发送一个包含 'plans_data' 列表的 JSON 请求体。
    """
    response_data: ServiceResult

    try:
        data = json.loads(request.body)
        plans_data = data.get('plans_data') # 从请求体中获取计划数据列表

        if plans_data is None:
            response_data = {"code": 300, "message": "请求体中缺少 'plans_data' 字段。", "data": None}
            return JsonResponse(response_data, status=400)

        # 调用服务层函数处理所有逻辑
        response_data = create_or_update_plans(username=request.user.id, plans_data=plans_data)

    except json.JSONDecodeError:
        response_data = {"code": 300, "message": "无效的JSON格式", "data": None}
        return JsonResponse(response_data, status=400)
    
    http_status = 200 if response_data['code'] == 200 else 400
    return JsonResponse(response_data, status=http_status)


@csrf_exempt

@require_http_methods(["GET"]) # 这个视图只接受 GET 请求，更符合 RESTful 风格
def list_plans_view(request):
    """
    一个统一的视图，用于获取用户的计划。
    可以通过 URL 查询参数来筛选星期，例如: /api/plan/list/?day=1
    """
    response_data: ServiceResult

    # 从 URL 查询参数中获取 day_of_week
    day_of_week_str = request.GET.get('day')
    day_of_week = None
    
    if day_of_week_str:
        try:
            day_of_week = int(day_of_week_str)
            if not 1 <= day_of_week <= 7:
                 response_data = {"code": 300, "message": "参数 'day' 必须是 1 到 7 之间的整数。", "data": None}
                 return JsonResponse(response_data, status=400)
        except (ValueError, TypeError):
            response_data = {"code": 300, "message": "参数 'day' 必须是一个整数。", "data": None}
            return JsonResponse(response_data, status=400)

    # 调用服务层函数
    response_data = get_user_plans(username=request.user.id, day_of_week=day_of_week)
    
    http_status = 200 if response_data['code'] == 200 else 400
    return JsonResponse(response_data, status=http_status)
