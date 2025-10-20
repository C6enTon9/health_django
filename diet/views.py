# diet/views.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from .services import (
    get_all_foods,
    add_food_to_meal,
    remove_food_from_meal,
    get_daily_meals,
    update_food_weight
)
from core.types import ServiceResult


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_foods_view(request):
    """
    获取所有食物列表

    请求参数: 无

    返回示例:
    {
        "code": 200,
        "message": "获取食物列表成功",
        "data": {
            "foods": [
                {
                    "id": 1,
                    "name": "米饭",
                    "category": "主食",
                    "calories": 116,
                    "protein": 2.6,
                    ...
                }
            ]
        }
    }
    """
    response_data = get_all_foods()
    http_status = 200 if response_data['code'] == 200 else 400
    return JsonResponse(response_data, status=http_status)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_food_view(request):
    """
    向餐次添加食物

    请求参数:
    {
        "meal_type": "breakfast",  # breakfast/lunch/dinner
        "food_id": 1,
        "weight": 200,  # 克
        "meal_date": "2025-10-16"  # 可选,默认今天
    }

    返回示例:
    {
        "code": 200,
        "message": "添加食物成功",
        "data": {
            "meal_food_id": 1,
            "food_name": "米饭",
            "weight": 200,
            "calories": 232
        }
    }
    """
    try:
        data = json.loads(request.body)
        meal_type = data.get('meal_type')
        food_id = data.get('food_id')
        weight = data.get('weight')
        meal_date = data.get('meal_date')

        if not meal_type or not food_id or not weight:
            response_data: ServiceResult = {
                "code": 300,
                "message": "缺少必要参数: meal_type, food_id, weight",
                "data": None
            }
            return JsonResponse(response_data, status=400)

        if meal_type not in ['breakfast', 'lunch', 'dinner']:
            response_data: ServiceResult = {
                "code": 300,
                "message": "meal_type必须是breakfast/lunch/dinner之一",
                "data": None
            }
            return JsonResponse(response_data, status=400)

        response_data = add_food_to_meal(
            user_id=request.user.id,
            meal_type=meal_type,
            food_id=food_id,
            weight=float(weight),
            meal_date=meal_date
        )

        http_status = 200 if response_data['code'] == 200 else 400
        return JsonResponse(response_data, status=http_status)

    except (json.JSONDecodeError, ValueError) as e:
        response_data: ServiceResult = {
            "code": 400,
            "message": f"请求格式错误: {e}",
            "data": None
        }
        return JsonResponse(response_data, status=400)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def remove_food_view(request):
    """
    从餐次中删除食物

    请求参数:
    {
        "meal_food_id": 1
    }

    返回示例:
    {
        "code": 200,
        "message": "删除食物成功",
        "data": null
    }
    """
    try:
        data = json.loads(request.body)
        meal_food_id = data.get('meal_food_id')

        if not meal_food_id:
            response_data: ServiceResult = {
                "code": 300,
                "message": "缺少必要参数: meal_food_id",
                "data": None
            }
            return JsonResponse(response_data, status=400)

        response_data = remove_food_from_meal(
            user_id=request.user.id,
            meal_food_id=meal_food_id
        )

        http_status = 200 if response_data['code'] == 200 else 400
        return JsonResponse(response_data, status=http_status)

    except (json.JSONDecodeError, ValueError) as e:
        response_data: ServiceResult = {
            "code": 400,
            "message": f"请求格式错误: {e}",
            "data": None
        }
        return JsonResponse(response_data, status=400)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_daily_meals_view(request):
    """
    获取每日餐次记录

    请求参数:
    {
        "meal_date": "2025-10-16"  # 可选,默认今天
    }

    返回示例:
    {
        "code": 200,
        "message": "获取每日餐次成功",
        "data": {
            "date": "2025-10-16",
            "meals": {
                "breakfast": {
                    "foods": [
                        {
                            "meal_food_id": 1,
                            "food_id": 1,
                            "name": "米饭",
                            "weight": 200,
                            "calories": 232,
                            "protein": 5.2,
                            "carbohydrates": 51.8,
                            "fat": 0.6
                        }
                    ],
                    "total_calories": 232,
                    "total_protein": 5.2,
                    "total_carbs": 51.8,
                    "total_fat": 0.6
                },
                "lunch": {...},
                "dinner": {...}
            },
            "daily_total_calories": 1500
        }
    }
    """
    try:
        data = json.loads(request.body) if request.body else {}
        meal_date = data.get('meal_date')

        response_data = get_daily_meals(
            user_id=request.user.id,
            meal_date=meal_date
        )

        http_status = 200 if response_data['code'] == 200 else 400
        return JsonResponse(response_data, status=http_status)

    except (json.JSONDecodeError, ValueError) as e:
        response_data: ServiceResult = {
            "code": 400,
            "message": f"请求格式错误: {e}",
            "data": None
        }
        return JsonResponse(response_data, status=400)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_food_weight_view(request):
    """
    更新食物重量

    请求参数:
    {
        "meal_food_id": 1,
        "weight": 300  # 新的重量(克)
    }

    返回示例:
    {
        "code": 200,
        "message": "更新重量成功",
        "data": {
            "weight": 300,
            "calories": 348
        }
    }
    """
    try:
        data = json.loads(request.body)
        meal_food_id = data.get('meal_food_id')
        weight = data.get('weight')

        if not meal_food_id or not weight:
            response_data: ServiceResult = {
                "code": 300,
                "message": "缺少必要参数: meal_food_id, weight",
                "data": None
            }
            return JsonResponse(response_data, status=400)

        response_data = update_food_weight(
            user_id=request.user.id,
            meal_food_id=meal_food_id,
            new_weight=float(weight)
        )

        http_status = 200 if response_data['code'] == 200 else 400
        return JsonResponse(response_data, status=http_status)

    except (json.JSONDecodeError, ValueError) as e:
        response_data: ServiceResult = {
            "code": 400,
            "message": f"请求格式错误: {e}",
            "data": None
        }
        return JsonResponse(response_data, status=400)
