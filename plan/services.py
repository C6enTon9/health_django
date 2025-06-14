# plan/services.py

from django.db import transaction
# --- FINAL FIX: Import get_user_model() instead of the User model directly ---
from django.contrib.auth import get_user_model
from .models import Plan
from core.types import ServiceResult
from typing import List, Dict, Any, Optional

@transaction.atomic
def create_or_update_plans(
    user_id: int, plans_data: List[Dict[str, Any]]
) -> ServiceResult:
    """
    A robust service to create or update one or more plans using the project's
    active user model.
    """
    # --- FINAL FIX: Get the correct User model for this project ---
    User = get_user_model()

    if not isinstance(plans_data, list) or not all(
        isinstance(p, dict) for p in plans_data
    ):
        return { "code": 300, "message": "Input data format is incorrect, a list of plan dictionaries is required.", "data": None }

    created_count = 0
    updated_count = 0
    errors = []

    try:
        # --- FINAL FIX: Use the correct User model to fetch the instance ---
        user_instance = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return {"code": 404, "message": f"User with ID {user_id} does not exist.", "data": None}

    for i, plan_data in enumerate(plans_data):
        plan_id = plan_data.get("id")
        title = plan_data.get("title")
        day_of_week = plan_data.get("day_of_week")
        start_time = plan_data.get("start_time")
        end_time = plan_data.get("end_time")

        if not all([title, day_of_week, start_time, end_time]):
            errors.append(f"Plan #{i+1} is missing required information (title, day_of_week, start_time, end_time).")
            continue

        try:
            data_to_save = {
                "title": title,
                "day_of_week": day_of_week,
                "start_time": start_time,
                "end_time": end_time,
                "description": plan_data.get("description", ""),
                "is_completed": plan_data.get("is_completed", False),
            }

            if plan_id:
                # Update logic uses user_id for filtering
                updated_rows = Plan.objects.filter(id=plan_id, user_id=user_id).update(**data_to_save)
                if updated_rows > 0:
                    updated_count += 1
                else:
                    errors.append(f"Plan with ID {plan_id} does not exist or you do not have permission to modify it.")
            else:
                # Create logic uses the user instance, which is best practice
                Plan.objects.create(user=user_instance, **data_to_save)
                created_count += 1

        except Exception as e:
            errors.append(f"An error occurred while processing plan #{i+1}: {e}")
    
    if not errors and (created_count > 0 or updated_count > 0):
        message_parts = []
        if created_count > 0: message_parts.append(f"Successfully created {created_count} new plan(s)")
        if updated_count > 0: message_parts.append(f"Successfully updated {updated_count} plan(s)")
        return {"code": 200, "message": ", ".join(message_parts) + ".", "data": {"created": created_count, "updated": updated_count}}
    elif errors:
        return {"code": 400, "message": "Operation failed with errors:\n- " + "\n- ".join(errors), "data": {"errors": errors}}
    else:
        return {"code": 300, "message": "No valid plan information was provided for processing.", "data": None}


def get_user_plans(user_id: int, day_of_week: Optional[int] = None) -> ServiceResult:
    """
    Gets the user's plans. This function was already correct as it uses user_id directly
    and doesn't need the User model. It is kept here for completeness.
    """
    try:
        plans_query = Plan.objects.filter(user_id=user_id)
        if day_of_week is not None:
            plans_query = plans_query.filter(day_of_week=day_of_week)

        plans_list = list(
            plans_query.values(
                "id", "title", "description", "day_of_week", 
                "start_time", "end_time", "is_completed",
            )
        )
        
        for plan in plans_list:
            if plan.get('start_time') and hasattr(plan['start_time'], 'strftime'):
                plan['start_time'] = plan['start_time'].strftime('%H:%M')
            if plan.get('end_time') and hasattr(plan['end_time'], 'strftime'):
                plan['end_time'] = plan['end_time'].strftime('%H:%M')

        return {
            "code": 200,
            "message": "Plans retrieved successfully." if plans_list else "You do not have any relevant plans.",
            "data": {"plans": plans_list, "count": len(plans_list)},
        }
    except Exception as e:
        return {"code": 500, "message": f"An error occurred while fetching plans: {e}", "data": None}
