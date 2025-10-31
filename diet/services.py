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


def batch_add_foods_to_meal(
    user_id: int,
    meal_type: str,
    meal_date: str,
    total_calories: float,
    total_protein: float,
    total_carbs: float,
    total_fat: float,
    foods: List[Dict[str, Any]]
) -> ServiceResult:
    """
    批量添加食物到餐次记录

    Args:
        user_id: 用户ID
        meal_type: 餐次类型 (breakfast/lunch/dinner)
        meal_date: 日期(YYYY-MM-DD格式)
        total_calories: 该餐次总热量
        total_protein: 该餐次总蛋白质
        total_carbs: 该餐次总碳水化合物
        total_fat: 该餐次总脂肪
        foods: 食物数组，每个元素包含:
            - name: 食物名称
            - weight: 重量(克)
            - calories: 热量
            - protein: 蛋白质
            - carbohydrates: 碳水化合物
            - fat: 脂肪

    Returns:
        ServiceResult: 包含操作结果的字典
    """
    try:
        # 处理日期
        try:
            meal_date_obj = datetime.strptime(meal_date, '%Y-%m-%d').date()
        except ValueError:
            return {"code": 300, "message": "日期格式错误,应为YYYY-MM-DD", "data": None}

        # 验证meal_type
        valid_meal_types = ['breakfast', 'lunch', 'dinner']
        if meal_type not in valid_meal_types:
            return {"code": 300, "message": f"餐次类型错误,应为{valid_meal_types}之一", "data": None}

        # 验证foods数组
        if not foods or not isinstance(foods, list):
            return {"code": 300, "message": "foods参数必须为非空数组", "data": None}

        # 获取或创建餐次记录
        meal_record, created = MealRecord.objects.get_or_create(
            user_id=user_id,
            meal_date=meal_date_obj,
            meal_type=meal_type,
            defaults={
                'total_calories': total_calories,
                'total_protein': total_protein,
                'total_carbs': total_carbs,
                'total_fat': total_fat,
            }
        )

        # 如果餐次记录已存在,更新总计
        if not created:
            meal_record.total_calories = total_calories
            meal_record.total_protein = total_protein
            meal_record.total_carbs = total_carbs
            meal_record.total_fat = total_fat
            meal_record.save()

        # 批量创建食物项
        meal_food_items = []
        for food_data in foods:
            # 验证必需字段
            required_fields = ['name', 'weight', 'calories', 'protein', 'carbohydrates', 'fat']
            missing_fields = [field for field in required_fields if field not in food_data]
            if missing_fields:
                return {
                    "code": 300,
                    "message": f"食物数据缺少必需字段: {', '.join(missing_fields)}",
                    "data": None
                }

            meal_food_item = MealFoodItem(
                meal_record=meal_record,
                food_item=None,  # 不关联FoodItem
                food_item_name=food_data['name'],
                weight=food_data['weight'],
                calories=food_data['calories'],
                protein=food_data['protein'],
                carbohydrates=food_data['carbohydrates'],
                fat=food_data['fat']
            )
            meal_food_items.append(meal_food_item)

        # 批量插入数据库
        MealFoodItem.objects.bulk_create(meal_food_items)

        return {
            "code": 200,
            "message": f"成功添加{len(meal_food_items)}个食物项到{meal_record.get_meal_type_display()}",
            "data": {
                "meal_record_id": meal_record.id,
                "meal_type": meal_type,
                "meal_date": meal_date,
                "foods_count": len(meal_food_items),
                "total_calories": total_calories,
                "total_protein": total_protein,
                "total_carbs": total_carbs,
                "total_fat": total_fat,
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"批量添加食物时发生错误: {e}")
        return {"code": 500, "message": "服务器内部错误", "data": None}


def get_diet_suggestion(user_id: int, days: int = 7) -> ServiceResult:
    """
    根据用户最近的饮食记录和健康信息生成饮食建议(返回一整段文字)

    Args:
        user_id: 用户ID
        days: 分析最近多少天的数据,默认7天
    """
    try:
        from datetime import timedelta
        from django.db.models import Avg, Sum

        # 获取用户健康信息
        try:
            user_info = Information.objects.get(user_id=user_id)
        except Information.DoesNotExist:
            return {"code": 400, "message": "请先完善个人健康信息", "data": None}

        # 计算推荐营养素
        recommended_macros = calculate_recommended_macros(user_id)
        if not recommended_macros:
            return {"code": 400, "message": "无法计算推荐营养素配比", "data": None}

        # 获取最近N天的饮食记录
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)

        meal_records = MealRecord.objects.filter(
            user_id=user_id,
            meal_date__gte=start_date,
            meal_date__lte=end_date
        )

        if not meal_records.exists():
            return {
                "code": 400,
                "message": f"最近{days}天没有饮食记录,请先添加饮食记录",
                "data": None
            }

        # 统计分析
        daily_stats = meal_records.values('meal_date').annotate(
            daily_calories=Sum('total_calories'),
            daily_protein=Sum('total_protein'),
            daily_carbs=Sum('total_carbs'),
            daily_fat=Sum('total_fat')
        )

        avg_calories = sum(d['daily_calories'] for d in daily_stats) / len(daily_stats) if daily_stats else 0
        avg_protein = sum(d['daily_protein'] for d in daily_stats) / len(daily_stats) if daily_stats else 0
        avg_carbs = sum(d['daily_carbs'] for d in daily_stats) / len(daily_stats) if daily_stats else 0
        avg_fat = sum(d['daily_fat'] for d in daily_stats) / len(daily_stats) if daily_stats else 0

        # 分析各餐次情况
        breakfast_count = meal_records.filter(meal_type='breakfast').count()

        # 生成建议文本
        suggestion_parts = []

        # 开头
        suggestion_parts.append(f"根据您最近{days}天的饮食记录分析:")

        # 1. 热量建议
        target_calories = user_info.daily_calories
        calorie_diff = avg_calories - target_calories
        calorie_diff_percent = (calorie_diff / target_calories * 100) if target_calories > 0 else 0

        suggestion_parts.append(f"\n您的平均每日热量摄入为{round(avg_calories, 1)}千卡,目标值为{target_calories}千卡。")

        if abs(calorie_diff_percent) < 5:
            suggestion_parts.append("热量摄入与目标接近,请继续保持!")
        elif calorie_diff > 0:
            suggestion_parts.append(f"热量摄入超出目标{round(abs(calorie_diff), 1)}千卡({round(abs(calorie_diff_percent), 1)}%),建议适当减少主食和油脂摄入。")
        else:
            suggestion_parts.append(f"热量摄入低于目标{round(abs(calorie_diff), 1)}千卡({round(abs(calorie_diff_percent), 1)}%),建议适当增加营养摄入,避免过度节食。")

        # 2. 蛋白质建议
        protein_diff = avg_protein - recommended_macros['protein']
        protein_diff_percent = (protein_diff / recommended_macros['protein'] * 100)

        suggestion_parts.append(f"\n蛋白质平均摄入{round(avg_protein, 1)}g/天,推荐值为{round(recommended_macros['protein'], 1)}g/天。")

        if abs(protein_diff_percent) < 10:
            suggestion_parts.append("蛋白质摄入符合推荐值。")
        elif protein_diff < 0:
            suggestion_parts.append("蛋白质摄入不足,建议增加鸡胸肉、鱼类、豆制品等优质蛋白来源。")
        else:
            suggestion_parts.append("蛋白质摄入充足,注意适量即可,过量摄入可能增加肾脏负担。")

        # 3. 碳水化合物建议
        carbs_diff_percent = (avg_carbs - recommended_macros['carbohydrates']) / recommended_macros['carbohydrates'] * 100

        suggestion_parts.append(f"\n碳水化合物平均摄入{round(avg_carbs, 1)}g/天,推荐值为{round(recommended_macros['carbohydrates'], 1)}g/天。")

        if abs(carbs_diff_percent) < 10:
            suggestion_parts.append("碳水化合物摄入比例合理。")
        elif carbs_diff_percent > 10:
            suggestion_parts.append("碳水化合物摄入偏高,建议减少精制米面,增加粗粮和蔬菜比例。")
        else:
            suggestion_parts.append("碳水化合物摄入偏低,适量碳水是能量来源,建议合理摄入全谷物。")

        # 4. 脂肪建议
        fat_diff_percent = (avg_fat - recommended_macros['fat']) / recommended_macros['fat'] * 100

        suggestion_parts.append(f"\n脂肪平均摄入{round(avg_fat, 1)}g/天,推荐值为{round(recommended_macros['fat'], 1)}g/天。")

        if abs(fat_diff_percent) < 10:
            suggestion_parts.append("脂肪摄入比例适中。")
        elif fat_diff_percent > 10:
            suggestion_parts.append("脂肪摄入偏高,建议减少油炸食品,选择蒸煮烹饪方式。")
        else:
            suggestion_parts.append("脂肪摄入偏低,适量健康脂肪(如坚果、橄榄油)对健康有益。")

        # 5. 餐次建议
        if breakfast_count < days * 0.7:
            suggestion_parts.append("\n建议规律吃早餐,早餐对新陈代谢和一天的精力都很重要。")

        # 6. 根据健康目标的建议
        if user_info.target:
            if "减肥" in user_info.target or "减脂" in user_info.target:
                suggestion_parts.append("\n针对您的减脂目标:建议控制总热量摄入,增加蛋白质比例,适量运动,避免过度节食。")
            elif "增肌" in user_info.target:
                suggestion_parts.append("\n针对您的增肌目标:建议适当提高蛋白质摄入(1.6-2.2g/kg体重),配合力量训练。")
            elif "维持" in user_info.target:
                suggestion_parts.append("\n针对您的维持目标:继续保持均衡饮食和规律运动习惯即可。")

        # 结尾
        suggestion_parts.append("\n\n保持健康的饮食习惯,祝您早日达成目标!")

        # 合并成一整段文字
        suggestion_text = "".join(suggestion_parts)

        return {
            "code": 200,
            "message": "生成饮食建议成功",
            "data": {
                "suggestion": suggestion_text
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"生成饮食建议时发生错误: {e}")
        return {"code": 500, "message": "服务器内部错误", "data": None}
