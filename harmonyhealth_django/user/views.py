from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .models import User
import json

def register(request):
    """
    用户注册接口
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
            
        # 检查用户是否存在
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'code': 401,
                'message': '用户不存在'
            })
            
        # 验证用户
        user = authenticate(request, username=user_id, password=password)
        if user is None:
            return JsonResponse({
                'code': 401,
                'message': '用户ID或密码错误',
                'debug': {
                    'user_id': user_id,
                    'user_password_length': len(password) if password else 0
                }
            })
            
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