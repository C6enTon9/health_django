import os
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, JSONParser
from pathlib import Path
from .services import FoodAnalysisService, NutritionCalculationService

# 临时图片存储目录
TEMP_DIR = Path(__file__).resolve().parent.parent.parent / "temp"
TEMP_DIR.mkdir(exist_ok=True)


class FoodRecognitionView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        # 1. 检查是否上传图片
        if "image" not in request.FILES:
            return JsonResponse({"error": "请上传图片文件"}, status=400)

        image_file = request.FILES["image"]

        # 2. 保存图片到临时目录（仅保存，不处理编码）
        try:
            temp_filename = f"food_{os.urandom(10).hex()}.jpg"
            temp_path = TEMP_DIR / temp_filename

            with open(temp_path, "wb") as f:
                for chunk in image_file.chunks():
                    f.write(chunk)
        except Exception as e:
            return JsonResponse({"error": f"图片保存失败：{str(e)}"}, status=500)

        # 3. 调用服务层（传递临时文件路径，由服务层处理编码）
        service = FoodAnalysisService()
        result = service.analyze_image(temp_path)  # 传入路径而非编码

        # 4. 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)

        # 5. 返回结果
        return JsonResponse(result)


# 新增：营养计算视图（接收食物名称和重量，调用AI计算热量）
class NutritionCalculationView(APIView):
    parser_classes = [JSONParser]  # 处理JSON格式请求（手机端传来的食物列表）

    def post(self, request):
        # 1. 验证请求数据格式
        if "foods" not in request.data:
            return JsonResponse({"error": "请求缺少foods字段（格式：[{name: str, weight: float}, ...]）"}, status=400)

        food_list = request.data["foods"]
        if not isinstance(food_list, list):
            return JsonResponse({"error": "foods必须是数组格式"}, status=400)

        # 验证每个食物项的结构
        for idx, item in enumerate(food_list):
            if not isinstance(item, dict):
                return JsonResponse({"error": f"foods第{idx}项必须是对象"}, status=400)
            if "name" not in item or not isinstance(item["name"], str):
                return JsonResponse({"error": f"foods第{idx}项缺少有效的name字段（字符串）"}, status=400)
            if "weight" not in item or not isinstance(item["weight"], (int, float)) or item["weight"] <= 0:
                return JsonResponse({"error": f"foods第{idx}项缺少有效的weight字段（正数）"}, status=400)

        # 2. 调用营养计算服务
        service = NutritionCalculationService()
        result = service.calculate_nutrition(food_list)

        # 3. 返回计算结果
        return JsonResponse(result)