# user/views.py

import json
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from typing import Tuple, Dict, Any, Optional, cast
from rest_framework.authtoken.models import Token
from core.types import ServiceResult
from .services import register_user
from django.contrib.auth.models import AbstractBaseUser # 导入User的基类
from .models import User
# --- 1. 创建一个通用的辅助函数来解析认证请求 ---
def _parse_auth_request(request: HttpRequest) -> Tuple[Optional[Dict[str, Any]], Optional[JsonResponse]]:
    """
    一个内部辅助函数，用于解析包含 username 和 password 的请求。
    - 如果成功，返回 (data, None)。
    - 如果失败，返回 (None, error_response)。
    """
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            error_response_data: ServiceResult = {"code": 300, "message": "用户名和密码不能为空", "data": None}
            return None, JsonResponse(error_response_data, status=400)
        
        return data, None

    except json.JSONDecodeError:
        error_response_data: ServiceResult = {"code": 300, "message": "无效的JSON格式", "data": None}
        return None, JsonResponse(error_response_data, status=400)


@csrf_exempt
@require_POST
def register_view(request: HttpRequest):
    """处理用户注册请求，所有返回均遵循 ServiceResult 格式。"""
    
    data, error_response = _parse_auth_request(request)
    if error_response:
        return error_response

    # --- 2. 关键修改点：添加一个 'if data:' 块 ---
    # 在这个块内部，类型检查器知道 data 不再是 None，因此可以安全地访问其键。
    if data:
        response_data = register_user(username=data['username'], password=data['password'])
        http_status = 200 if response_data['code'] == 200 else 400
        return JsonResponse(response_data, status=http_status)

    # 逻辑上虽然走不到这里，但为了代码的完整性和类型检查，提供一个后备返回。
    fallback_response: ServiceResult = {"code": 500, "message": "服务器发生未知错误", "data": None}
    return JsonResponse(fallback_response, status=500)


@csrf_exempt
@require_POST
def login_view(request: HttpRequest):
    """处理用户登录请求，所有返回均遵循 ServiceResult 格式。"""
    
    data, error_response = _parse_auth_request(request)
    if error_response:
        return error_response
    
    # --- 3. 关键修改点：同样使用 'if data:' 块 ---
    if data:
        user = authenticate(request, username=data['username'], password=data['password'])

        if user is not None:
            auth_login(request, user)
            # 使用 cast 明确告知 user 拥有 username 属性，或者直接依赖 django-stubs
            logged_in_user = cast(User, user)
            token, created = Token.objects.get_or_create(user=user)
            response_data: ServiceResult = {
                "code": 200,
                "message": "登录成功",
                "data": {"username": logged_in_user.username,"token": token.key}
            }
            return JsonResponse(response_data, status=200)
        else:
            response_data: ServiceResult = {
                "code": 400,
                "message": "用户名或密码错误",
                "data": None
            }
            return JsonResponse(response_data, status=400)

    fallback_response: ServiceResult = {"code": 500, "message": "服务器发生未知错误", "data": None}
    return JsonResponse(fallback_response, status=500)


@csrf_exempt
@require_POST
def logout_view(request: HttpRequest):
    """处理用户登出请求，返回遵循 ServiceResult 格式。"""
    
    auth_logout(request)
    
    response_data: ServiceResult = {"code": 200, "message": "已成功登出", "data": None}
    return JsonResponse(response_data, status=200)