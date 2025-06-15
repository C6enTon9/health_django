# plan/views.py

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from .services import get_recent_plans
from .services import create_or_update_plans, get_user_plans, get_over_number, get_workout
from core.types import ServiceResult

@api_view(['POST']) # 只允许 POST 请求
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def manage_plans_view(request):
    """
    一个统一的视图，用于创建或更新一个或多个计划。
    现在这是一个受 DRF 保护的视图，能正确处理 Token 认证。
    """
    # DRF 会自动处理 JSON 解析，我们直接从 request.data 获取
    # 我们期望前端直接发送 plan 对象，或者包含 id 的 plan 对象
    plan_data = request.data

    if not isinstance(plan_data, dict):
        return Response({"code": 300, "message": "请求体必须是一个JSON对象。"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 调用我们之前已经修改好的服务层函数
        # 服务函数 create_or_update_plans 接收 **kwargs
        response_data: ServiceResult = create_or_update_plans(user_id=request.user.id, **plan_data)
        
        http_status = status.HTTP_200_OK
        # 先获取 data 字典，并确保它不是 None
        data_dict = response_data.get('data')
        if response_data['code'] == 200 and data_dict is not None and data_dict.get('created'):
            http_status = status.HTTP_201_CREATED
        return Response(response_data, status=http_status)

    except Exception as e:
        # 捕获服务层可能发生的意外错误
        return Response({"code": 500, "message": f"处理计划时发生内部错误: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET']) # 只允许 GET 请求
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def list_plans_view(request):
    """
    一个统一的视图，用于获取用户的计划。
    现在这是一个受 DRF 保护的视图。
    可以通过 URL 查询参数来筛选星期，例如: /api/plan/list/?day_of_week=1
    """
    # 从 URL 查询参数中获取 day_of_week
    day_of_week_str = request.query_params.get('day_of_week') # DRF 中使用 request.query_params
    day_of_week = None
    
    if day_of_week_str:
        try:
            day_of_week = int(day_of_week_str)
            if not 1 <= day_of_week <= 7:
                 return Response({"code": 300, "message": "参数 'day_of_week' 必须是 1 到 7 之间的整数。"}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"code": 300, "message": "参数 'day_of_week' 必须是一个整数。"}, status=status.HTTP_400_BAD_REQUEST)

    # 调用服务层函数，并使用正确的参数名 'user_id'
    response_data: ServiceResult = get_user_plans(user_id=request.user.id, day_of_week=day_of_week)
    
    # DRF 的 Response 会自动处理大部分情况，但我们也可以根据 code 明确设置
    http_status = status.HTTP_200_OK if response_data['code'] == 200 else status.HTTP_400_BAD_REQUEST
    return Response(response_data, status=http_status)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def recent_plans_view(request):
    """
    获取用户最近的计划记录。
    可以通过查询参数 ?limit=N 来指定获取的数量。
    """
    try:
        limit_str = request.query_params.get('limit', '5') # 默认获取5条
        limit = int(limit_str)
    except (ValueError, TypeError):
        limit = 5 # 如果参数无效，使用默认值

    response_data = get_recent_plans(user_id=request.user.id, limit=limit)
    
    return Response(response_data, status=status.HTTP_200_OK if response_data['code'] == 200 else status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_over_num_view(request):


    response_data = get_over_number(user_id=request.user.id)

    return Response(response_data, status=status.HTTP_200_OK if response_data['code'] == 200 else status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_workout_view(request):


    response_data = get_workout(user_id=request.user.id)

    return Response(response_data, status=status.HTTP_200_OK if response_data['code'] == 200 else status.HTTP_400_BAD_REQUEST)