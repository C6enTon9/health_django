# diet/models.py

from django.db import models
from django.conf import settings


class FoodItem(models.Model):
    """
    食物营养信息库
    """
    name = models.CharField(max_length=200, verbose_name="食物名称", db_index=True)
    category = models.CharField(max_length=50, verbose_name="食物分类")

    # 营养成分 (per 100g)
    calories = models.FloatField(verbose_name="热量(kcal/100g)")
    protein = models.FloatField(verbose_name="蛋白质(g/100g)", default=0)
    carbohydrates = models.FloatField(verbose_name="碳水化合物(g/100g)", default=0)
    fat = models.FloatField(verbose_name="脂肪(g/100g)", default=0)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "食物信息"
        verbose_name_plural = "食物信息"

    def __str__(self):
        return f"{self.name} ({self.category})"


class MealRecord(models.Model):
    """
    用户餐次记录
    """
    MEAL_TYPE_CHOICES = [
        ('breakfast', '早餐'),
        ('lunch', '午餐'),
        ('dinner', '晚餐'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='meal_records',
        verbose_name="用户"
    )

    meal_type = models.CharField(
        max_length=20,
        choices=MEAL_TYPE_CHOICES,
        verbose_name="餐次类型"
    )

    meal_date = models.DateField(verbose_name="就餐日期", db_index=True)

    # 营养汇总 (该餐次的总计)
    total_calories = models.FloatField(verbose_name="总热量(kcal)", default=0)
    total_protein = models.FloatField(verbose_name="总蛋白质(g)", default=0)
    total_carbs = models.FloatField(verbose_name="总碳水化合物(g)", default=0)
    total_fat = models.FloatField(verbose_name="总脂肪(g)", default=0)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "餐次记录"
        verbose_name_plural = "餐次记录"
        ordering = ['-meal_date', 'meal_type']
        unique_together = [['user', 'meal_date', 'meal_type']]
        indexes = [
            models.Index(fields=['user', 'meal_date']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_meal_type_display()} ({self.meal_date})"

    def calculate_totals(self):
        """
        计算该餐次所有食物的营养总和
        """
        items = self.food_items.all()
        self.total_calories = sum(item.calories for item in items)
        self.total_protein = sum(item.protein for item in items)
        self.total_carbs = sum(item.carbohydrates for item in items)
        self.total_fat = sum(item.fat for item in items)
        self.save(update_fields=['total_calories', 'total_protein', 'total_carbs', 'total_fat', 'updated_at'])


class MealFoodItem(models.Model):
    """
    餐次中的具体食物项
    """
    meal_record = models.ForeignKey(
        MealRecord,
        on_delete=models.CASCADE,
        related_name='food_items',
        verbose_name="所属餐次"
    )

    food_item = models.ForeignKey(
        FoodItem,
        on_delete=models.CASCADE,
        verbose_name="食物信息"
    )

    # 实际重量
    weight = models.FloatField(verbose_name="重量(g)")

    # 该食物项的营养成分(根据实际重量计算)
    calories = models.FloatField(verbose_name="热量(kcal)")
    protein = models.FloatField(verbose_name="蛋白质(g)", default=0)
    carbohydrates = models.FloatField(verbose_name="碳水化合物(g)", default=0)
    fat = models.FloatField(verbose_name="脂肪(g)", default=0)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "餐次食物项"
        verbose_name_plural = "餐次食物项"

    def __str__(self):
        return f"{self.food_item.name} - {self.weight}g"

    def calculate_nutrition(self):
        """
        根据食物基础信息和实际重量计算营养成分
        """
        ratio = self.weight / 100.0  # 基础数据是per 100g
        self.calories = round(self.food_item.calories * ratio, 2)
        self.protein = round(self.food_item.protein * ratio, 2)
        self.carbohydrates = round(self.food_item.carbohydrates * ratio, 2)
        self.fat = round(self.food_item.fat * ratio, 2)
