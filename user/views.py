from rest_framework.views import APIView
from rest_framework.response import Response  # Corrected import
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import check_password
from .models import User
from django.http import Http404, JsonResponse
from django.contrib.auth import authenticate, login
import json

def register(request):
    """
    用户注册接口
    POST请求，需要提供：
    {
        "user_id": "用户ID",
        "password": "密码"
    }
    """
    if request.method != 'POST':
        return JsonResponse({'code': 400, 'message': '只支持POST请求'})
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        password = data.get('password')
        
        # 验证数据
        if not user_id or not password:
            return JsonResponse({'code': 400, 'message': '用户ID和密码不能为空'})
            
        # 检查用户是否已存在
        if User.objects.filter(user_id=user_id).exists():
            return JsonResponse({'code': 400, 'message': '用户ID已存在'})
            
        # 创建新用户
        user = User.objects.create_user(user_id=user_id, password=password)
        
        return JsonResponse({
            'code': 200,
            'message': '注册成功',
            'data': {'user_id': user.user_id}
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'code': 400, 'message': '无效的JSON数据'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})

def login_view(request):
    """
    用户登录接口
    POST请求，需要提供：
    {
        "user_id": "用户ID",
        "password": "密码"
    }
    """
    if request.method != 'POST':
        return JsonResponse({'code': 400, 'message': '只支持POST请求'})
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        password = data.get('password')
        
        # 验证数据
        if not user_id or not password:
            return JsonResponse({'code': 400, 'message': '用户ID和密码不能为空'})
            
        # 验证用户
        user = authenticate(request, username=user_id, password=password)
        if user is None:
            return JsonResponse({'code': 401, 'message': '用户ID或密码错误'})
            
        # 登录用户
        login(request, user)
        
        return JsonResponse({
            'code': 200,
            'message': '登录成功',
            'data': {'user_id': user.user_id}
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'code': 400, 'message': '无效的JSON数据'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})