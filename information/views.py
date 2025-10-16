# information/views.py

import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .services import update_user_info, get_user_info, get_health_metrics, ALLOWED_FIELDS
from core.types import ServiceResult

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_attribute_view(request, attribute_name: str):
    """
    一个通用的视图，处理对单个属性的更新。
    'attribute_name' 从 URL 路径中捕获。
    """
    response_data: ServiceResult

    # 安全检查：确保要更新的字段在白名单内
    if attribute_name not in ALLOWED_FIELDS:
        response_data = {"code": 400, "message": f"不允许更新属性'{attribute_name}'", "data": None}
        return JsonResponse(response_data, status=400)

    try:
        data = json.loads(request.body)
        # [推荐修改] 始终从一个固定的 'value' 键中获取值
        value = data.get('value')
        
        # 增加一个检查，确保 'value' 存在
        if value is None:
            raise AttributeError("'value' key not found in request body")

    except (json.JSONDecodeError, AttributeError) as e:
        response_data = {"code": 400, "message": f"请求体格式错误: {e}", "data": None}
        return JsonResponse(response_data, status=400)

    # 构建要传递给服务层的 updates 字典
    updates = {attribute_name: value}
    
    # 调用服务层
    response_data = update_user_info(user_id=request.user.id, updates=updates)
    
    http_status = 200 if response_data['code'] == 200 else 400
    return JsonResponse(response_data, status=http_status)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def get_attribute_view(request, attribute_name: str):
    """
    一个通用的视图，处理对单个属性的查询。
    'attribute_name' 从 URL 路径中捕获。
    """
    response_data: ServiceResult
    
    # 安全检查：确保要查询的字段在白名单内
    if attribute_name not in ALLOWED_FIELDS:
        response_data = {"code": 400, "message": f"不允许查询属性'{attribute_name}'", "data": None}
        return JsonResponse(response_data, status=400)

    # 构建要传递给服务层的 attributes 列表
    attributes = [attribute_name]
    
    # 调用服务层
    response_data = get_user_info(user_id=request.user.id, attributes=attributes)
    http_status = 200 if response_data['code'] == 200 else 400
    return JsonResponse(response_data, status=http_status)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_health_metrics_view(request):
    """
    获取用户的健康指标（BMI、BMR、每日推荐热量等）
    """
    response_data = get_health_metrics(user_id=request.user.id)
    http_status = 200 if response_data['code'] == 200 else 400
    return JsonResponse(response_data, status=http_status)
