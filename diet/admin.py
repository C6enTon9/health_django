# diet/admin.py

from django.contrib import admin
from .models import FoodItem, MealRecord, MealFoodItem


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'calories', 'protein', 'carbohydrates', 'fat']
    list_filter = ['category']
    search_fields = ['name', 'category']


class MealFoodItemInline(admin.TabularInline):
    model = MealFoodItem
    extra = 0


@admin.register(MealRecord)
class MealRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'meal_type', 'meal_date', 'total_calories']
    list_filter = ['meal_type', 'meal_date']
    search_fields = ['user__username']
    inlines = [MealFoodItemInline]


@admin.register(MealFoodItem)
class MealFoodItemAdmin(admin.ModelAdmin):
    list_display = ['meal_record', 'food_item', 'weight', 'calories']
    list_filter = ['meal_record__meal_type']
