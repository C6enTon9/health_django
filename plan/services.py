from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from .models import Plan
from core.types import ServiceResult
from typing import Any, Optional

@transaction.atomic
def create_or_update_plans(user_id: int, **kwargs: Any) -> ServiceResult:
    """
    一个健壮的服务，用于创建或部分更新一个计划。
    - 如果提供了 'id'，则执行部分更新。
    - 如果未提供 'id'，则执行创建，并校验所有必要字段。
    """
    plan_data = kwargs
    plan_id = plan_data.get("id")

    # 将 User 的定义提到最前面，以解决 Pylance 警告并统一获取
    User = get_user_model()

    if plan_id:
        # --- 更新逻辑 ---
        # 对于更新，我们不再检查所有字段，只更新传入的字段
        
        # 从 plan_data 中移除 id，剩下的就是待更新的数据
        update_data = plan_data.copy()
        update_data.pop('id', None)

        if not update_data:
            return {"code": 300, "message": "没有提供任何要更新的字段。", "data": None}

        try:
            # 使用 filter().update() 进行高效更新
            updated_rows = Plan.objects.filter(id=plan_id, user_id=user_id).update(**update_data)
            
            if updated_rows > 0:
                return {"code": 200, "message": "计划更新成功。", "data": {"updated": 1}}
            else:
                return {"code": 404, "message": f"ID为 {plan_id} 的计划不存在或您无权修改。", "data": None}
        except Exception as e:
            return {"code": 500, "message": f"更新计划时发生数据库错误: {e}", "data": None}

    else:
        # --- 创建逻辑 ---
        # 对于创建，我们仍然需要检查所有核心字段
        title = plan_data.get("title")
        day_of_week = plan_data.get("day_of_week")
        start_time = plan_data.get("start_time")
        end_time = plan_data.get("end_time")

        if not all([title, day_of_week, start_time, end_time]):
            return {"code": 300, "message": "创建新计划时缺少必要信息（标题、星期、开始/结束时间）。", "data": None}
        
        try:
            user_instance = User.objects.get(id=user_id)
            # 确保创建时不传入 id
            plan_data.pop('id', None)
            new_plan = Plan.objects.create(user=user_instance, **plan_data)
            return {"code": 201, "message": f"成功创建了新计划 '{new_plan.title}'。", "data": {"created": 1, "id": new_plan.id}}
        
        except User.DoesNotExist:
            return {"code": 404, "message": f"ID为 {user_id} 的用户不存在。", "data": None}
        except Exception as e:
            return {"code": 500, "message": f"创建计划时发生数据库错误: {e}", "data": None}


def get_user_plans(user_id: int, day_of_week: Optional[int] = None) -> ServiceResult:
    """
    获取用户的周常计划。
    """
    try:
        plans_query = Plan.objects.filter(user_id=user_id)
        if day_of_week is not None:
            plans_query = plans_query.filter(day_of_week=day_of_week)

        plans_list = list(
            plans_query.order_by('start_time').values(
                "id", "title", "description", "day_of_week", 
                "start_time", "end_time", "is_completed",
            )
        )
        
        for plan in plans_list:
            # 将 TimeField 对象格式化为 HH:MM 字符串
            if plan.get('start_time') and hasattr(plan['start_time'], 'strftime'):
                plan['start_time'] = plan['start_time'].strftime('%H:%M')
            if plan.get('end_time') and hasattr(plan['end_time'], 'strftime'):
                plan['end_time'] = plan['end_time'].strftime('%H:%M')

        return {
            "code": 200,
            "message": "计划获取成功。" if plans_list else "您还没有任何相关计划。",
            "data": {"plans": plans_list, "count": len(plans_list)},
        }
    except Exception as e:
        return {"code": 500, "message": f"获取计划时发生错误: {e}", "data": None}
    
def delete_plan(user_id: int, plan_id: int) -> ServiceResult:
    """
    根据 plan_id 删除一个属于指定用户的计划。
    """
    if not plan_id:
        return {"code": 300, "message": "删除计划时必须提供 plan_id。", "data": None}

    try:
        # 首先查找这个计划，确保它存在并且属于当前用户
        plan_to_delete = Plan.objects.get(id=plan_id, user_id=user_id)
        
        # 如果找到了，就删除它
        plan_to_delete.delete()
        
        return {"code": 200, "message": f"ID为 {plan_id} 的计划已成功删除。", "data": {"deleted": 1}}

    except Plan.DoesNotExist:
        # 如果找不到，说明 plan_id 不存在或不属于该用户
        return {"code": 404, "message": f"ID为 {plan_id} 的计划不存在或您无权删除。", "data": None}
    except Exception as e:
        return {"code": 500, "message": f"删除计划时发生错误: {e}", "data": None}