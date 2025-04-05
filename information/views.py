from django.shortcuts import render
from .models import Information
from django.http import JsonResponse
import json


def upd_height(request):
    # 获取数据
    data = json.loads(request.body)
    height = data.get("height")
    user_id = data.get("user_id")
    # 验证数据
    if height is None or user_id is None:
        return JsonResponse({"code": 300, "message": "缺少必要参数"})
    # 业务逻辑
    information = Information.objects.get(user_id=user_id)
    if not information:
        return JsonResponse({"code": 400, "message": "用户不存在"})
    information.height = height
    information.save()
    return JsonResponse(
        {"code": 200, "message": "身高更新成功", "data": {"height": height}}
    )


def get_height(request):
    # 获取数据
    data = json.loads(request.body)
    user_id = data.get("user_id")
    # 验证数据
    if user_id is None:
        return JsonResponse({"code": 300, "message": "缺少必要参数"})
    # 业务逻辑
    information = Information.objects.get(user_id=user_id)
    if not information:
        return JsonResponse({"code": 400, "message": "用户不存在"})
    height = information.height
    return JsonResponse(
        {"code": 200, "message": "身高获取成功", "data": {"height": height}}
    )


def upd_weight(request):
    # 获取数据
    data = json.loads(request.body)
    weight = data.get("weight")
    user_id = data.get("user_id")
    # 验证数据
    if weight is None or user_id is None:
        return JsonResponse({"code": 300, "message": "缺少必要参数"})
    if weight <= 0 or weight > 500:
        return JsonResponse({"code": 300, "message": "体重不合法"})
    # 业务逻辑
    information = Information.objects.get(user_id=user_id)
    if not information:
        return JsonResponse({"code": 400, "message": "用户不存在"})
    information.weight = weight
    information.save()
    return JsonResponse(
        {"code": 200, "message": "体重更新成功", "data": {"weight": weight}}
    )


def get_weight(request):
    # 获取数据
    data = json.loads(request.body)
    user_id = data.get("user_id")
    # 验证数据
    if user_id is None:
        return JsonResponse({"code": 300, "message": "缺少必要参数"})
    # 业务逻辑
    information = Information.objects.get(user_id=user_id)
    if not information:
        return JsonResponse({"code": 400, "message": "用户不存在"})
    weight = information.weight
    return JsonResponse(
        {"code": 200, "message": "体重获取成功", "data": {"weight": weight}}
    )


def upd_age(request):
    # 获取数据
    data = json.loads(request.body)
    age = data.get("age")
    user_id = data.get("user_id")
    # 验证数据
    if age is None or user_id is None:
        return JsonResponse({"code": 300, "message": "缺少必要参数"})
    if age < 0 or age > 150:
        return JsonResponse({"code": 300, "message": "年龄不合法"})
    # 业务逻辑
    information = Information.objects.get(user_id=user_id)
    if not information:
        return JsonResponse({"code": 400, "message": "用户不存在"})
    information.age = age
    information.save()
    return JsonResponse({"code": 200, "message": "年龄更新成功", "data": {"age": age}})


def get_age(request):
    # 获取数据
    data = json.loads(request.body)
    user_id = request.GET.get("user_id")
    # 验证数据
    if user_id is None:
        return JsonResponse({"code": 300, "message": "缺少必要参数"})
    # 业务逻辑
    information = Information.objects.get(user_id=user_id)
    if not information:
        return JsonResponse({"code": 400, "message": "用户不存在"})
    age = information.age
    return JsonResponse({"code": 200, "message": "年龄获取成功", "data": {"age": age}})


def upd_information(request):
    # 获取数据
    data = json.loads(request.body)
    information = data.get("information")
    user_id = data.get("user_id")
    # 验证数据
    if information is None or user_id is None:
        return JsonResponse({"code": 300, "message": "缺少必要参数"})
    # 业务逻辑
    information_obj = Information.objects.get(user_id=user_id)
    if not information_obj:
        return JsonResponse({"code": 400, "message": "用户不存在"})
    information_obj.information = information
    information_obj.save()
    return JsonResponse(
        {"code": 200, "message": "信息更新成功", "data": {"information": information}}
    )


def get_information(request):
    # 获取数据
    data = json.loads(request.body)
    user_id = request.GET.get("user_id")
    # 验证数据
    if user_id is None:
        return JsonResponse({"code": 300, "message": "缺少必要参数"})
    # 业务逻辑
    information_obj = Information.objects.get(user_id=user_id)
    if not information_obj:
        return JsonResponse({"code": 400, "message": "用户不存在"})
    information = information_obj.information
    return JsonResponse(
        {"code": 200, "message": "信息获取成功", "data": {"information": information}}
    )


def upd_target(request):
    # 获取数据
    data = json.loads(request.body)
    target = data.get("target")
    user_id = data.get("user_id")
    # 验证数据
    if target is None or user_id is None:
        return JsonResponse({"code": 300, "message": "缺少必要参数"})
    # 业务逻辑
    information_obj = Information.objects.get(user_id=user_id)
    if not information_obj:
        return JsonResponse({"code": 400, "message": "用户不存在"})
    information_obj.target = target
    information_obj.save()
    return JsonResponse(
        {"code": 200, "message": "目标更新成功", "data": {"target": target}}
    )


def get_target(request):
    # 获取数据
    data = json.loads(request.body)
    user_id = request.GET.get("user_id")
    # 验证数据
    if user_id is None:
        return JsonResponse({"code": 300, "message": "缺少必要参数"})
    # 业务逻辑
    information_obj = Information.objects.get(user_id=user_id)
    if not information_obj:
        return JsonResponse({"code": 400, "message": "用户不存在"})
    target = information_obj.target
    return JsonResponse(
        {"code": 200, "message": "目标获取成功", "data": {"target": target}}
    )
