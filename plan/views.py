from django.shortcuts import render

def get_plan():
    """
    根据个人信息获取计划
    1.根据请求获取用户
    2.数据库查询用户信息
    3.与deepseek对话获取计划
    4.加入计划数据库
    5.返回“生成计划成功”
    """
    pass

def upd_plan():
    """
    更新计划
    1.根据请求获取用户以及新信息
    2.数据库查询用户信息并更新
    3.与deepseek对话获取新计划
    4.加入计划数据库
    5.返回“更新计划成功”
    """
    pass