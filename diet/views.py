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
    update_food_weight,
    get_diet_suggestion,
    batch_add_foods_to_meal
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


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_diet_suggestion_view(request):
    """
    获取饮食建议

    请求参数:
    {
        "days": 7  # 可选,分析最近多少天的数据,默认7天
    }

    返回示例:
    {
        "code": 200,
        "message": "生成饮食建议成功",
        "data": {
            "analysis_period": "最近7天",
            "record_days": 5,
            "current_intake": {
                "avg_calories": 1850.5,
                "avg_protein": 75.2,
                "avg_carbs": 220.3,
                "avg_fat": 60.1
            },
            "recommended_intake": {
                "calories": 2000,
                "protein": 87.5,
                "carbs": 262.5,
                "fat": 61.1
            },
            "meal_stats": {
                "breakfast": {
                    "count": 5,
                    "avg_calories": 450.0
                },
                "lunch": {
                    "count": 5,
                    "avg_calories": 700.0
                },
                "dinner": {
                    "count": 4,
                    "avg_calories": 600.0
                }
            },
            "suggestions": [
                {
                    "type": "热量摄入",
                    "status": "良好",
                    "message": "您的平均每日热量摄入为1850.5千卡,与目标值2000千卡接近,请继续保持!"
                },
                {
                    "type": "蛋白质",
                    "status": "不足",
                    "message": "蛋白质摄入75.2g/天,低于推荐值。建议增加鸡胸肉、鱼类、豆制品等优质蛋白来源。"
                }
            ]
        }
    }
    """
    try:
        data = json.loads(request.body) if request.body else {}
        days = data.get('days', 7)

        # 验证days参数
        try:
            days = int(days)
            if days < 1 or days > 30:
                response_data: ServiceResult = {
                    "code": 300,
                    "message": "days参数必须在1-30之间",
                    "data": None
                }
                return JsonResponse(response_data, status=400)
        except (ValueError, TypeError):
            response_data: ServiceResult = {
                "code": 300,
                "message": "days参数必须是整数",
                "data": None
            }
            return JsonResponse(response_data, status=400)

        response_data = get_diet_suggestion(
            user_id=request.user.id,
            days=days
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
def batch_add_foods_view(request):
    """
    批量添加食物到餐次

    请求参数:
    {
        "meal_type": "lunch",  # breakfast/lunch/dinner
        "meal_date": "2025-10-31",
        "total_calories": 366,
        "total_protein": 37.3,
        "total_carbs": 43.3,
        "total_fat": 4.2,
        "foods": [
            {
                "name": "米饭",
                "weight": 150,
                "calories": 174,
                "protein": 4.0,
                "carbohydrates": 39.0,
                "fat": 0.3
            },
            {
                "name": "鸡胸肉",
                "weight": 100,
                "calories": 165,
                "protein": 31.0,
                "carbohydrates": 0,
                "fat": 3.6
            }
        ]
    }

    返回示例:
    {
        "code": 200,
        "message": "成功添加2个食物项到午餐",
        "data": {
            "meal_record_id": 1,
            "meal_type": "lunch",
            "meal_date": "2025-10-31",
            "foods_count": 2,
            "total_calories": 366,
            "total_protein": 37.3,
            "total_carbs": 43.3,
            "total_fat": 4.2
        }
    }
    """
    try:
        data = json.loads(request.body)

        # 获取必需参数
        meal_type = data.get('meal_type')
        meal_date = data.get('meal_date')
        total_calories = data.get('total_calories')
        total_protein = data.get('total_protein')
        total_carbs = data.get('total_carbs')
        total_fat = data.get('total_fat')
        foods = data.get('foods')

        # 验证必需参数
        if not all([meal_type, meal_date, foods]):
            response_data: ServiceResult = {
                "code": 300,
                "message": "缺少必要参数: meal_type, meal_date, foods",
                "data": None
            }
            return JsonResponse(response_data, status=400)

        if total_calories is None or total_protein is None or total_carbs is None or total_fat is None:
            response_data: ServiceResult = {
                "code": 300,
                "message": "缺少必要参数: total_calories, total_protein, total_carbs, total_fat",
                "data": None
            }
            return JsonResponse(response_data, status=400)

        # 验证meal_type
        if meal_type not in ['breakfast', 'lunch', 'dinner']:
            response_data: ServiceResult = {
                "code": 300,
                "message": "meal_type必须是breakfast/lunch/dinner之一",
                "data": None
            }
            return JsonResponse(response_data, status=400)

        # 验证foods格式
        if not isinstance(foods, list) or len(foods) == 0:
            response_data: ServiceResult = {
                "code": 300,
                "message": "foods必须是非空数组",
                "data": None
            }
            return JsonResponse(response_data, status=400)

        # 调用服务函数
        response_data = batch_add_foods_to_meal(
            user_id=request.user.id,
            meal_type=meal_type,
            meal_date=meal_date,
            total_calories=float(total_calories),
            total_protein=float(total_protein),
            total_carbs=float(total_carbs),
            total_fat=float(total_fat),
            foods=foods
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

