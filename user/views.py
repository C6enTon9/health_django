from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import User

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = request.data
            user_id = data.get('user_id')
            password = data.get('password')
            
            # 验证必填字段
            if not user_id or not password:
                return Response({
                    'code': 400,
                    'message': '用户ID和密码不能为空'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # 检查用户是否已存在
            if User.objects.filter(user_id=user_id).exists():
                return Response({
                    'code': 400,
                    'message': '用户ID已存在'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # 创建新用户
            user = User(user_id=user_id)
            user.set_password(password)
            user.save()
            
            # 创建token
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'code': 200,
                'message': '注册成功',
                'data': {
                    'user_id': user.user_id,
                    'token': token.key
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            data = request.data
            user_id = data.get('user_id')
            password = data.get('password')
            
            # 验证数据
            if not user_id or not password:
                return Response({
                    'code': 400,
                    'message': '用户ID和密码不能为空'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # 验证用户
            try:
                user = User.objects.get(user_id=user_id)
                if not user.check_password(password):
                    return Response({
                        'code': 401,
                        'message': '用户ID或密码错误'
                    }, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({
                    'code': 401,
                    'message': '用户ID或密码错误'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 创建或获取token
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'code': 200,
                'message': '登录成功',
                'data': {
                    'user_id': user.user_id,
                    'token': token.key
                }
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    def post(self, request):
        try:
            # 删除用户token
            request.user.auth_token.delete()
            return Response({
                'code': 200,
                'message': '退出登录成功'
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)