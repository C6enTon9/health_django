# information/services.py

from .models import Information
from django.core.exceptions import ObjectDoesNotExist
from typing import Dict, Any, List, Optional
from core.types import ServiceResult

ALLOWED_FIELDS = {'height', 'weight', 'age', 'information', 'target'}


# --- 核心修改点 ---
# 修改了函数签名，让它能接收任意关键字参数
def update_user_info(user_id: int, **kwargs: Any) -> ServiceResult:
    """
    通用更新工具，通过 user_id 操作。
    现在它接受任意数量的关键字参数作为要更新的字段。
    例如: update_user_info(user_id=1, height=180, weight=75)
    """
    # **kwargs 会是一个字典，比如 {'height': 180}，我们直接用它作为 updates
    updates = kwargs
    
    if not isinstance(updates, dict) or not updates:
         return {"code": 300, "message": "没有提供任何需要更新的信息。", "data": None}

    try:
        info_obj = Information.objects.get(user_id=user_id)
        
        updated_fields = []
        for field, value in updates.items():
            if field in ALLOWED_FIELDS:
                setattr(info_obj, field, value)
                updated_fields.append(field)

        if not updated_fields:
            return {"code": 300, "message": "提供的字段均不被支持更新。", "data": None}

        info_obj.save(update_fields=updated_fields)
        
        updated_data = {field: getattr(info_obj, field) for field in updated_fields}
        return {"code": 200, "message": "信息更新成功", "data": updated_data}

    except ObjectDoesNotExist:
        return {"code": 400, "message": "用户的信息记录不存在", "data": None}
    except Exception as e:
        print(f"更新用户信息时发生错误: {e}")
        return {"code": 500, "message": "服务器内部错误", "data": None}


# get_user_info 函数保持不变
def get_user_info(user_id: int, attributes: Optional[List[str]] = None) -> ServiceResult:
    """
    通用查询工具，通过 user_id 操作。
    如果 attributes 未提供，则返回所有信息。
    """
    try:
        info_obj = Information.objects.get(user_id=user_id)
        
        if not attributes:
            attributes_to_fetch = list(ALLOWED_FIELDS)
        else:
            attributes_to_fetch = attributes

        results_data = {}
        for field in attributes_to_fetch:
            if field in ALLOWED_FIELDS:
                results_data[field] = getattr(info_obj, field, None)
        
        if not results_data:
            return {"code": 400, "message": "请求查询的字段均不被支持。", "data": None}

        return {"code": 200, "message": "信息获取成功", "data": results_data}

    except ObjectDoesNotExist:
        return {"code": 400, "message": "用户的信息记录不存在", "data": None}
    except Exception as e:
        print(f"获取用户信息时发生错误: {e}")
        return {"code": 500, "message": "服务器内部错误", "data": None}