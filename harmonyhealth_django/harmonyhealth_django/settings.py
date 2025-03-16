# ... 其他设置 ...

# 自定义用户模型
AUTH_USER_MODEL = 'user.User'

# 认证后端
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# ... 其他设置 ... 