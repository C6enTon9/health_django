# user/services.py

from django.db import transaction
from django.contrib.auth import get_user_model
from information.models import Information
from core.types import ServiceResult # 从 core app 导入标准返回类型

# 获取当前项目激活的 User 模型 (在我们的例子中是 user.User)
User = get_user_model() 

@transaction.atomic # 确保整个函数在数据库事务中执行，保证数据一致性
def register_user(username: str, password: str) -> ServiceResult:
    """
    处理用户注册的核心逻辑。
    - 校验输入数据。
    - 检查用户是否已存在。
    - 在一个事务中创建 User 和关联的 Information 记录。
    - 所有返回路径都遵循 ServiceResult 格式。
    """
    # 1. 输入数据校验
    if not username or not password:
        return {"code": 300, "message": "用户名和密码不能为空", "data": None}
    
    if len(password) < 8:
        return {"code": 300, "message": "为了安全，密码长度不能少于8位", "data": None}
    
    # 2. 检查用户是否已存在
    if User.objects.filter(username=username).exists():
        return {"code": 400, "message": "用户名已存在", "data": None}

    # 3. 业务逻辑与数据库操作
    try:
        # 使用 Django 推荐的 create_user 方法，它会自动处理密码哈希
        new_user = User.objects.create_user(username=username, password=password)#type:ignore
        
        # 创建关联的 Information 记录
        # 如果 Information 的 user 字段是 OneToOneField(primary_key=True)，
        # 这种创建方式是正确的
        Information.objects.create(user=new_user)

        # 4. 返回成功的 ServiceResult
        return {
            "code": 200, 
            "message": "注册成功", 
            "data": {"username": new_user.username}
        }
    except Exception as e:
        # 捕获所有可能的异常（例如数据库连接错误）
        # 因为有 @transaction.atomic，如果这里出错，上面创建的用户会被自动回滚
        print(f"注册时发生内部错误: {e}") # 在后台记录详细错误以供调试
        
        # 5. 返回服务器错误的 ServiceResult
        return {
            "code": 500, 
            "message": "注册过程中发生未知错误，请稍后重试", 
            "data": None
        }

# login_user 函数已被移除，因为它的逻辑更适合放在视图层，
# 与 Django 的 authenticate 和 auth_login 函数直接结合使用。
# 这避免了 service 和 view 之间的重复验证。