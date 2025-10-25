# information/views.py

import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .services import update_user_info, get_user_info, get_health_metrics, get_all_user_info, ALLOWED_FIELDS
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


# ==================== 旧版兼容接口 ====================
# 这些接口保持向后兼容，使用旧的请求体格式（包含username字段）

@csrf_exempt
@require_POST
def upd_height_view(request):
    """旧版接口: 更新身高"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        height = data.get('height')

        from user.models import User
        user = User.objects.get(username=username)
        response_data = update_user_info(user_id=user.id, height=height)
    except User.DoesNotExist:
        response_data = {"code": 400, "message": "用户不存在", "data": None}
    except Exception as e:
        response_data = {"code": 400, "message": str(e), "data": None}

    return JsonResponse(response_data)


@csrf_exempt
@require_POST
def get_height_view(request):
    """旧版接口: 获取身高"""
    try:
        data = json.loads(request.body)
        username = data.get('username')

        from user.models import User
        user = User.objects.get(username=username)
        response_data = get_user_info(user_id=user.id, attributes=['height'])
    except User.DoesNotExist:
        response_data = {"code": 400, "message": "用户不存在", "data": None}
    except Exception as e:
        response_data = {"code": 400, "message": str(e), "data": None}

    return JsonResponse(response_data)


@csrf_exempt
@require_POST
def upd_weight_view(request):
    """旧版接口: 更新体重"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        weight = data.get('weight')

        from user.models import User
        user = User.objects.get(username=username)
        response_data = update_user_info(user_id=user.id, weight=weight)
    except User.DoesNotExist:
        response_data = {"code": 400, "message": "用户不存在", "data": None}
    except Exception as e:
        response_data = {"code": 400, "message": str(e), "data": None}

    return JsonResponse(response_data)


@csrf_exempt
@require_POST
def get_weight_view(request):
    """旧版接口: 获取体重"""
    try:
        data = json.loads(request.body)
        username = data.get('username')

        from user.models import User
        user = User.objects.get(username=username)
        response_data = get_user_info(user_id=user.id, attributes=['weight'])
    except User.DoesNotExist:
        response_data = {"code": 400, "message": "用户不存在", "data": None}
    except Exception as e:
        response_data = {"code": 400, "message": str(e), "data": None}

    return JsonResponse(response_data)


@csrf_exempt
@require_POST
def upd_age_view(request):
    """旧版接口: 更新年龄"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        age = data.get('age')

        from user.models import User
        user = User.objects.get(username=username)
        response_data = update_user_info(user_id=user.id, age=age)
    except User.DoesNotExist:
        response_data = {"code": 400, "message": "用户不存在", "data": None}
    except Exception as e:
        response_data = {"code": 400, "message": str(e), "data": None}

    return JsonResponse(response_data)


@csrf_exempt
@require_POST
def get_age_view(request):
    """旧版接口: 获取年龄"""
    try:
        data = json.loads(request.body)
        username = data.get('username')

        from user.models import User
        user = User.objects.get(username=username)
        response_data = get_user_info(user_id=user.id, attributes=['age'])
    except User.DoesNotExist:
        response_data = {"code": 400, "message": "用户不存在", "data": None}
    except Exception as e:
        response_data = {"code": 400, "message": str(e), "data": None}

    return JsonResponse(response_data)


@csrf_exempt
@require_POST
def upd_information_view(request):
    """旧版接口: 更新个人信息"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        information = data.get('information')

        from user.models import User
        user = User.objects.get(username=username)
        response_data = update_user_info(user_id=user.id, information=information)
    except User.DoesNotExist:
        response_data = {"code": 400, "message": "用户不存在", "data": None}
    except Exception as e:
        response_data = {"code": 400, "message": str(e), "data": None}

    return JsonResponse(response_data)


@csrf_exempt
@require_POST
def get_information_view(request):
    """旧版接口: 获取个人信息"""
    try:
        data = json.loads(request.body)
        username = data.get('username')

        from user.models import User
        user = User.objects.get(username=username)
        response_data = get_user_info(user_id=user.id, attributes=['information'])
    except User.DoesNotExist:
        response_data = {"code": 400, "message": "用户不存在", "data": None}
    except Exception as e:
        response_data = {"code": 400, "message": str(e), "data": None}

    return JsonResponse(response_data)


@csrf_exempt
@require_POST
def upd_target_view(request):
    """旧版接口: 更新目标"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        target = data.get('target')

        from user.models import User
        user = User.objects.get(username=username)
        response_data = update_user_info(user_id=user.id, target=target)
    except User.DoesNotExist:
        response_data = {"code": 400, "message": "用户不存在", "data": None}
    except Exception as e:
        response_data = {"code": 400, "message": str(e), "data": None}

    return JsonResponse(response_data)


@csrf_exempt
@require_POST
def get_target_view(request):
    """旧版接口: 获取目标"""
    try:
        data = json.loads(request.body)
        username = data.get('username')

        from user.models import User
        user = User.objects.get(username=username)
        response_data = get_user_info(user_id=user.id, attributes=['target'])
    except User.DoesNotExist:
        response_data = {"code": 400, "message": "用户不存在", "data": None}
    except Exception as e:
        response_data = {"code": 400, "message": str(e), "data": None}

    return JsonResponse(response_data)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_all_info_view(request):
    """
    获取用户的所有个人信息,包括饮食建议

    请求体参数:
    - days: 分析最近多少天的饮食数据(可选,默认7天)

    返回示例:
    {
        "code": 200,
        "message": "获取用户信息成功",
        "data": {
            "username": "test_user",
            "height": 175.0,
            "weight": 70.0,
            "age": 25,
            "gender": "male",
            "gender_display": "男",
            "target": "减肥",
            "information": "我是一名程序员",
            "target_calories": 2000.0,
            "bmi": 22.86,
            "bmi_category": "正常",
            "bmr": 1663.75,
            "daily_calories": 1996.5,
            "diet_suggestion": "根据您最近7天的饮食记录分析:..."
        }
    }
    """
    try:
        data = json.loads(request.body) if request.body else {}
        days = data.get('days', 7)  # 默认7天

        # 验证 days 参数
        if not isinstance(days, int) or days < 1 or days > 30:
            return JsonResponse(
                {"code": 300, "message": "参数 'days' 必须是 1 到 30 之间的整数", "data": None},
                status=400
            )
    except json.JSONDecodeError:
        days = 7  # 如果解析失败,使用默认值

    response_data = get_all_user_info(user_id=request.user.id, days=days)
    http_status = 200 if response_data['code'] == 200 else 400
    return JsonResponse(response_data, status=http_status)

