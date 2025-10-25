# plan/views.py

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from .services import get_recent_plans
from .services import (
    create_or_update_plans,
    get_user_plans,
    get_over_number,
    get_workout,
    delete_plan,
    delete_all_plans,
    create_bulk_plans
)
from core.types import ServiceResult

@api_view(['POST']) # 只允许 POST 请求
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def manage_plans_view(request):
    """
    统一的计划管理视图,支持创建、更新、删除、批量创建等操作。

    根据请求参数中的 action 字段来区分不同操作:
    - 无 action: 创建或更新计划
    - action="delete": 删除单个计划
    - action="delete_all": 批量删除计划
    - action="bulk_create": 批量创建计划
    """
    plan_data = request.data

    if not isinstance(plan_data, dict):
        return Response(
            {"code": 300, "message": "请求体必须是一个JSON对象。"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        action = plan_data.get('action')

        # 删除单个计划
        if action == 'delete':
            plan_id = plan_data.get('plan_id')
            if not plan_id:
                return Response(
                    {"code": 300, "message": "删除计划需要提供 plan_id 参数。"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            response_data: ServiceResult = delete_plan(
                user_id=request.user.id,
                plan_id=plan_id
            )
            http_status = status.HTTP_200_OK if response_data['code'] == 200 else status.HTTP_400_BAD_REQUEST
            return Response(response_data, status=http_status)

        # 批量删除计划
        elif action == 'delete_all':
            day_of_week = plan_data.get('day_of_week')
            response_data: ServiceResult = delete_all_plans(
                user_id=request.user.id,
                day_of_week=day_of_week
            )
            http_status = status.HTTP_200_OK if response_data['code'] == 200 else status.HTTP_400_BAD_REQUEST
            return Response(response_data, status=http_status)

        # 批量创建计划
        elif action == 'bulk_create':
            plans_data = plan_data.get('plans_data')
            if not plans_data or not isinstance(plans_data, list):
                return Response(
                    {"code": 300, "message": "批量创建需要提供 plans_data 数组参数。"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            response_data: ServiceResult = create_bulk_plans(
                user_id=request.user.id,
                plans_data=plans_data
            )
            http_status = status.HTTP_201_CREATED if response_data['code'] == 201 else status.HTTP_400_BAD_REQUEST
            return Response(response_data, status=http_status)

        # 创建或更新计划(默认行为)
        else:
            response_data: ServiceResult = create_or_update_plans(
                user_id=request.user.id,
                **plan_data
            )

            http_status = status.HTTP_200_OK
            data_dict = response_data.get('data')
            if response_data['code'] in [200, 201] and data_dict is not None and data_dict.get('created'):
                http_status = status.HTTP_201_CREATED
            elif response_data['code'] not in [200, 201]:
                http_status = status.HTTP_400_BAD_REQUEST

            return Response(response_data, status=http_status)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {"code": 500, "message": f"处理计划时发生内部错误: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET']) # 只允许 GET 请求
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def list_plans_view(request):
    """
    获取用户的计划列表(支持查询所有历史数据)

    查询参数:
    - day_of_week: 星期几(1-7)
    - created_after: 创建时间起始(YYYY-MM-DD)
    - created_before: 创建时间结束(YYYY-MM-DD)
    - limit: 返回数量限制
    - offset: 分页偏移量

    示例: /api/plan/list/?day_of_week=1&limit=20&offset=0
    """
    try:
        # 从 URL 查询参数中获取筛选条件
        day_of_week_str = request.query_params.get('day_of_week')
        created_after = request.query_params.get('created_after')
        created_before = request.query_params.get('created_before')
        limit_str = request.query_params.get('limit')
        offset_str = request.query_params.get('offset', '0')

        day_of_week = None
        limit = None
        offset = 0

        # 解析 day_of_week
        if day_of_week_str:
            try:
                day_of_week = int(day_of_week_str)
                if not 1 <= day_of_week <= 7:
                     return Response(
                         {"code": 300, "message": "参数 'day_of_week' 必须是 1 到 7 之间的整数。"},
                         status=status.HTTP_400_BAD_REQUEST
                     )
            except (ValueError, TypeError):
                return Response(
                    {"code": 300, "message": "参数 'day_of_week' 必须是一个整数。"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 解析 limit
        if limit_str:
            try:
                limit = int(limit_str)
                if limit < 1:
                    return Response(
                        {"code": 300, "message": "参数 'limit' 必须大于0。"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (ValueError, TypeError):
                return Response(
                    {"code": 300, "message": "参数 'limit' 必须是一个整数。"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 解析 offset
        try:
            offset = int(offset_str)
            if offset < 0:
                return Response(
                    {"code": 300, "message": "参数 'offset' 不能为负数。"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {"code": 300, "message": "参数 'offset' 必须是一个整数。"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 调用服务层函数
        response_data: ServiceResult = get_user_plans(
            user_id=request.user.id,
            day_of_week=day_of_week,
            created_after=created_after,
            created_before=created_before,
            limit=limit,
            offset=offset
        )

        http_status = status.HTTP_200_OK if response_data['code'] == 200 else status.HTTP_400_BAD_REQUEST
        return Response(response_data, status=http_status)

    except Exception as e:
        return Response(
            {"code": 500, "message": f"处理请求时发生错误: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

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