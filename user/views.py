from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .models import User
import json
from information.models import Information


def register(request):

    # 获取数据
    data = json.loads(request.body)
    user_id = data.get("user_id")
    password = data.get("password")

    # 验证数据
    if not user_id or not password:
        return JsonResponse({"code": 300, "message": "用户ID和密码不能为空"})

    # 业务逻辑
    if User.objects.filter(user_id=user_id).exists():
        return JsonResponse({"code": 400, "message": "用户ID已存在"})
    user = User.objects.create_user(user_id=user_id, password=password)
    information = Information.objects.create(
        user_id=user_id, information="", height=0, weight=0, age=0
    )
    return JsonResponse(
        {"code": 200, "message": "注册成功", "data": {"user_id": user.user_id}}
    )


def login(request):

    # 获取数据
    data = json.loads(request.body)
    user_id = data.get("user_id")
    password = data.get("password")

    # 验证数据
    if not user_id or not password:
        return JsonResponse({"code": 300, "message": "用户ID和密码不能为空"})

    # 业务逻辑
    user = User.objects.filter(user_id=user_id).first()
    if user is None:
        return JsonResponse({"code": 400, "message": "用户不存在"})
    if password != user.password:
        return JsonResponse({"code": 400, "message": "用户ID或密码错误"})
    return JsonResponse(
        {"code": 200, "message": "登录成功", "data": {"user_id": user.user_id}}
    )
