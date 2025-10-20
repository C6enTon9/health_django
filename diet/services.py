# diet/services.py

from .models import FoodItem, MealRecord, MealFoodItem
from information.models import Information
from django.core.exceptions import ObjectDoesNotExist
from typing import Dict, Any, List, Optional
from core.types import ServiceResult
from datetime import date, datetime
from django.db.models import Sum


def calculate_recommended_macros(user_id: int) -> Optional[Dict[str, float]]:
    """
    根据用户身体情况计算推荐的三大营养素配比

    营养素配比标准:
    - 蛋白质: 每日热量的15-20% (取中间值17.5%)
    - 碳水化合物: 每日热量的50-55% (取中间值52.5%)
    - 脂肪: 每日热量的25-30% (取中间值27.5%)

    转换系数:
    - 1g 蛋白质 = 4 kcal
    - 1g 碳水化合物 = 4 kcal
    - 1g 脂肪 = 9 kcal

    Returns:
        包含推荐蛋白质、碳水和脂肪克数的字典,如果用户信息不存在则返回None
    """
    try:
        info = Information.objects.get(user_id=user_id)
        daily_calories = info.daily_calories  # 使用用户的每日推荐热量(可能是自定义值)

        # 计算推荐的营养素克数
        recommended_protein = round((daily_calories * 0.175) / 4, 1)  # 17.5%的热量来自蛋白质
        recommended_carbs = round((daily_calories * 0.525) / 4, 1)    # 52.5%的热量来自碳水
        recommended_fat = round((daily_calories * 0.275) / 9, 1)      # 27.5%的热量来自脂肪

        return {
            'protein': recommended_protein,
            'carbohydrates': recommended_carbs,
            'fat': recommended_fat,
        }
    except Information.DoesNotExist:
        return None


def get_all_foods() -> ServiceResult:
    """
    获取所有食物列表
    """
    try:
        foods = FoodItem.objects.all().order_by('category', 'name')
        foods_data = []

        for food in foods:
            foods_data.append({
                'id': food.id,
                'name': food.name,
                'category': food.category,
                'calories': food.calories,
                'protein': food.protein,
                'carbohydrates': food.carbohydrates,
                'fat': food.fat,
            })

        return {
            "code": 200,
            "message": "获取食物列表成功",
            "data": {"foods": foods_data}
        }
    except Exception as e:
        print(f"获取食物列表时发生错误: {e}")
        return {"code": 500, "message": "服务器内部错误", "data": None}


def add_food_to_meal(user_id: int, meal_type: str, food_id: int, weight: float, meal_date: str = None) -> ServiceResult:
    """
    向指定餐次添加食物

    Args:
        user_id: 用户ID
        meal_type: 餐次类型 (breakfast/lunch/dinner)
        food_id: 食物ID
        weight: 重量(克)
        meal_date: 日期(YYYY-MM-DD格式), 默认为今天
    """
    try:
        # 获取食物信息
        food = FoodItem.objects.get(id=food_id)

        # 处理日期
        if meal_date:
            try:
                meal_date_obj = datetime.strptime(meal_date, '%Y-%m-%d').date()
            except ValueError:
                return {"code": 300, "message": "日期格式错误,应为YYYY-MM-DD", "data": None}
        else:
            meal_date_obj = date.today()

        # 获取或创建餐次记录
        meal_record, created = MealRecord.objects.get_or_create(
            user_id=user_id,
            meal_date=meal_date_obj,
            meal_type=meal_type
        )

        # 创建食物项
        meal_food_item = MealFoodItem(
            meal_record=meal_record,
            food_item=food,
            weight=weight
        )
        meal_food_item.calculate_nutrition()  # 计算营养成分
        meal_food_item.save()

        # 更新餐次总计
        meal_record.calculate_totals()

        return {
            "code": 200,
            "message": "添加食物成功",
            "data": {
                "meal_food_id": meal_food_item.id,
                "food_name": food.name,
                "weight": weight,
                "calories": meal_food_item.calories,
            }
        }

    except FoodItem.DoesNotExist:
        return {"code": 400, "message": "食物不存在", "data": None}
    except Exception as e:
        print(f"添加食物时发生错误: {e}")
        return {"code": 500, "message": "服务器内部错误", "data": None}


def remove_food_from_meal(user_id: int, meal_food_id: int) -> ServiceResult:
    """
    从餐次中删除食物

    Args:
        user_id: 用户ID
        meal_food_id: 餐次食物项ID
    """
    try:
        meal_food_item = MealFoodItem.objects.get(
            id=meal_food_id,
            meal_record__user_id=user_id
        )

        meal_record = meal_food_item.meal_record
        meal_food_item.delete()

        # 更新餐次总计
        meal_record.calculate_totals()

        return {
            "code": 200,
            "message": "删除食物成功",
            "data": None
        }

    except MealFoodItem.DoesNotExist:
        return {"code": 400, "message": "食物项不存在", "data": None}
    except Exception as e:
        print(f"删除食物时发生错误: {e}")
        return {"code": 500, "message": "服务器内部错误", "data": None}


def get_daily_meals(user_id: int, meal_date: str = None) -> ServiceResult:
    """
    获取某天的所有餐次记录

    Args:
        user_id: 用户ID
        meal_date: 日期(YYYY-MM-DD格式), 默认为今天
    """
    try:
        # 处理日期
        if meal_date:
            try:
                meal_date_obj = datetime.strptime(meal_date, '%Y-%m-%d').date()
            except ValueError:
                return {"code": 300, "message": "日期格式错误,应为YYYY-MM-DD", "data": None}
        else:
            meal_date_obj = date.today()

        # 获取该日期的所有餐次
        meal_records = MealRecord.objects.filter(
            user_id=user_id,
            meal_date=meal_date_obj
        ).prefetch_related('food_items__food_item')

        # 构建返回数据
        meals_data = {
            'breakfast': {'foods': [], 'total_calories': 0, 'total_protein': 0, 'total_carbs': 0, 'total_fat': 0},
            'lunch': {'foods': [], 'total_calories': 0, 'total_protein': 0, 'total_carbs': 0, 'total_fat': 0},
            'dinner': {'foods': [], 'total_calories': 0, 'total_protein': 0, 'total_carbs': 0, 'total_fat': 0},
        }

        daily_total_calories = 0
        daily_total_protein = 0
        daily_total_carbs = 0
        daily_total_fat = 0

        for meal_record in meal_records:
            meal_type = meal_record.meal_type

            # 获取该餐次的所有食物
            foods_list = []
            for food_item in meal_record.food_items.all():
                foods_list.append({
                    'meal_food_id': food_item.id,
                    'food_id': food_item.food_item.id,
                    'name': food_item.food_item.name,
                    'weight': round(food_item.weight, 1),
                    'calories': round(food_item.calories, 1),
                    'protein': round(food_item.protein, 1),
                    'carbohydrates': round(food_item.carbohydrates, 1),
                    'fat': round(food_item.fat, 1),
                })

            meals_data[meal_type] = {
                'foods': foods_list,
                'total_calories': round(meal_record.total_calories, 1),
                'total_protein': round(meal_record.total_protein, 1),
                'total_carbs': round(meal_record.total_carbs, 1),
                'total_fat': round(meal_record.total_fat, 1),
            }

            daily_total_calories += meal_record.total_calories
            daily_total_protein += meal_record.total_protein
            daily_total_carbs += meal_record.total_carbs
            daily_total_fat += meal_record.total_fat

        # 计算推荐的营养素配比
        recommended_macros = calculate_recommended_macros(user_id)

        response_data = {
            "date": meal_date_obj.strftime('%Y-%m-%d'),
            "meals": meals_data,
            "daily_total_calories": round(daily_total_calories, 1),
            "daily_total_protein": round(daily_total_protein, 1),
            "daily_total_carbs": round(daily_total_carbs, 1),
            "daily_total_fat": round(daily_total_fat, 1),
        }

        # 如果能获取到推荐值,则添加到响应中
        if recommended_macros:
            response_data["recommended_protein"] = recommended_macros['protein']
            response_data["recommended_carbs"] = recommended_macros['carbohydrates']
            response_data["recommended_fat"] = recommended_macros['fat']

        return {
            "code": 200,
            "message": "获取每日餐次成功",
            "data": response_data
        }

    except Exception as e:
        print(f"获取每日餐次时发生错误: {e}")
        return {"code": 500, "message": "服务器内部错误", "data": None}


def update_food_weight(user_id: int, meal_food_id: int, new_weight: float) -> ServiceResult:
    """
    更新餐次中食物的重量

    Args:
        user_id: 用户ID
        meal_food_id: 餐次食物项ID
        new_weight: 新的重量(克)
    """
    try:
        meal_food_item = MealFoodItem.objects.get(
            id=meal_food_id,
            meal_record__user_id=user_id
        )

        meal_food_item.weight = new_weight
        meal_food_item.calculate_nutrition()  # 重新计算营养成分
        meal_food_item.save()

        # 更新餐次总计
        meal_record = meal_food_item.meal_record
        meal_record.calculate_totals()

        return {
            "code": 200,
            "message": "更新重量成功",
            "data": {
                "weight": meal_food_item.weight,
                "calories": meal_food_item.calories,
            }
        }

    except MealFoodItem.DoesNotExist:
        return {"code": 400, "message": "食物项不存在", "data": None}
    except Exception as e:
        print(f"更新重量时发生错误: {e}")
        return {"code": 500, "message": "服务器内部错误", "data": None}
