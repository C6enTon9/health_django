from django.shortcuts import render
import json
from .models import Plan
from information.models import Information
from information.views import get_all_information
from django.http import JsonResponse
from ai.deepseek import chat
from ai.response2plan import parse_plans


def get_plan(request):
    # 获取数据
    data = json.loads(request.body)
    user_id = data.get("user_id")
    # 验证数据
    if user_id is None:
        return JsonResponse({"code": 300, "message": "缺少必要参数"})
    # 业务逻辑
    plans = Plan.objects.filter(user_id=user_id)
    if not plans:
        return JsonResponse({"code": 400, "message": "用户不存在"})
    return JsonResponse(
        {"code": 200, "message": "获取计划成功", "data": plans.values()}
    )


def upd_plan(request):
    # 获取数据
    data = json.loads(request.body)
    user_id = data.get("user_id")
    new_info = data.get("new_info")
    if new_info is None:
        new_info = ""
    # 检验数据
    if not user_id or not new_info:
        return JsonResponse({"code": 300, "message": "用户ID或新信息缺失"})
    # 业务逻辑
    information = Information.objects.get(user_id=user_id)
    if not information:
        return JsonResponse({"code": 400, "message": "用户不存在"})
    information.information = information.information + new_info
    information.save()
    message = get_all_information(user_id)
    make_plan(user_id, message)
    return JsonResponse({"code": 200, "message": "更新计划成功"})


def make_plan(user_id, information):
    plans = chat(user_id, information)
    plans = parse_plans(plans)
    # 将解析后的计划保存到数据库
    for plan in plans:
        plan_instance = Plan(
            user_id=user_id,
            thing=plan.thing,
            description=plan.description,
            day=plan.day,
            start_time=plan.start_time,
            end_time=plan.end_time,
            is_completed=False,
        )
        plan_instance.save()
    return JsonResponse({"code": 200, "message": "计划生成成功", "data": plans})
