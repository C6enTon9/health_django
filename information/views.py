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
