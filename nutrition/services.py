import json
import base64
from django.utils import timezone
from chat.services import client  # 导入公共OpenAI client
class FoodAnalysisService:
    def __init__(self):
        self.model = "gpt-4o"

    def analyze_image(self, image_path: str):
        """
        处理图片编码并调用API分析
        :param image_path: 临时图片文件的本地路径
        :return: 结构化分析结果
        """
        # 1. 先将图片转换为Base64编码（核心：服务层处理编码）
        image_base64 = self._encode_image(image_path)
        if not image_base64:
            return {"error": "图片编码失败"}

        # 2. 构建提示词
        prompt = """
        你需要分析图片中的食物，完成「识别-估算-计算-汇总」全流程，严格遵循以下规则：

        ### 一、食物识别要求
        1. 精准识别所有可见食物（包括主食、配菜、酱料等，如“白米饭”“煎鸡胸肉”“水煮西兰花”，避免模糊分类如“肉”“蔬菜”）。
        2. 对每种食物给出 **识别置信度**（格式：XX%，基于视觉匹配度，如“95%”表示高度确定，“60%”表示较低确定）。
        3. 若存在相似食物（如“普通米饭”vs“糙米饭”），优先选择更常见的类型，或标注“疑似XX”（如“疑似糙米饭，置信度70%”）。

        ### 二、份量估算要求
        1. 参考图片中的 **参照物**（如餐盘大小、筷子/勺子比例、手掌对比等）估算重量，单位统一为「克（g）」。
        2. 份量需符合日常逻辑（如“1碗米饭约150-200g”“1块牛排约150-200g”“1根香蕉约100-120g”），避免极端值（如10g、1000g）。
        3. 若食物被遮挡（仅露出部分），按“可见部分占比”估算整体重量（如“半块披萨可见，估算整体重量150g”）。

        ### 三、营养计算要求
        1. 营养数据基于 **每100克可食用部分** 计算，需符合常见食物的营养标准（参考权威数据库如USDA，避免明显错误）。
        2. 必算指标（单位：热量=千卡kcal，蛋白质/碳水/脂肪=克g）：
           - 热量：如米饭130kcal/100g、鸡胸肉165kcal/100g、西兰花34kcal/100g。
           - 蛋白质：如鸡胸肉31g/100g、鸡蛋13g/100g、牛奶3g/100g。
           - 碳水化合物：如米饭28.7g/100g、红薯27.9g/100g、苹果13.8g/100g。
           - 脂肪：如五花肉50g/100g、牛油果15g/100g、橄榄油100g/100g。
        3. 若食物烹饪方式影响营养（如“油炸”vs“水煮”），需调整数据（如“水煮鸡胸肉165kcal/100g”“油炸鸡胸肉250kcal/100g”）。

        ### 四、输出格式要求（必须为JSON，不可加额外文字）
        {
          "foods": [
            {
              "name": "食物全称（如“白米饭”“水煮西兰花”）",
              "confidence": "识别置信度（如“95%”）",
              "weight": 估算重量（数字，如150）,
              "calories": 热量（数字，保留1位小数，如195.0）,
              "protein": 蛋白质（数字，保留1位小数，如3.9）,
              "carbs": 碳水化合物（数字，保留1位小数，如43.1）,
              "fat": 脂肪（数字，保留1位小数，如0.5）,
              "note": "补充说明（如“疑似糙米饭”“部分遮挡，按整体估算”，无则填空字符串）"
            }
          ],
          "total": {
            "total_calories": 所有食物热量总和（数字，保留1位小数）,
            "total_protein": 所有食物蛋白质总和（数字，保留1位小数）,
            "total_carbs": 所有食物碳水总和（数字，保留1位小数）,
            "total_fat": 所有食物脂肪总和（数字，保留1位小数）
          },
          "analysis_time": "当前时间（格式：YYYY-MM-DD HH:MM:SS，如“2025-10-20 18:30:00”）"
        }

        ### 五、禁止事项
        1. 不可遗漏图片中的任何食物（即使是小份量酱料、坚果等）。
        2. 不可返回JSON以外的内容（如解释文字、换行符、注释）。
        3. 重量和营养数据不可为负数或0（除非食物确实无该成分，如纯瘦肉脂肪接近0可填0.0）。
        """

        # 3. 调用OpenAI API
        try:
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt.strip()},
                            {
                                "type": "image_url",
                                 "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ]
                # messages=[
                #     {
                #         "role": "user",
                #         "content": "Hello!"
                #     }
                # ]
            )
            # print(response.choices[0].message.content)
            # print(response.output_text)
            return self._process_response(response)

        except Exception as e:
            return {"error": f"API调用失败：{str(e)}"}

    def _encode_image(self, image_path: str) -> str:
        """图片编码处理（服务层内部方法）"""
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")  # 返回纯编码字符串
        except Exception as e:
            print(f"图片编码失败：{e}")
            return ""

    def _process_response(self, response):
        """解析结果并打印到控制台"""
        try:
            content = response.choices[0].message.content.strip()
            result = json.loads(content)

            # 打印结果
            print("\n" + "="*60)
            print(f"【分析时间】{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("【食物识别结果】")
            for food in result["foods"]:
                print(f"- {food['name']}（{food['confidence']}）：{food['weight']}g，{food['calories']}kcal")
                print(f"  营养：蛋白质{food['protein']}g | 碳水{food['carbs']}g | 脂肪{food['fat']}g")
            print("\n【总计】")
            print(f"总热量：{result['total']['total_calories']}kcal | 总蛋白质：{result['total']['total_protein']}g")
            print(f"总碳水：{result['total']['total_carbs']}g | 总脂肪：{result['total']['total_fat']}g")
            print("="*60 + "\n")

            return {"success": True, "data": result}

        except json.JSONDecodeError:
            return {"error": "模型返回非JSON格式", "raw_content": content}
        except KeyError as e:
            return {"error": f"结果缺失字段：{str(e)}", "raw_content": content}
        except Exception as e:
            return {"error": f"结果处理失败：{str(e)}", "raw_content": content}


class NutritionCalculationService:
    def calculate_nutrition(self, food_list: list):
        """
        调用OpenAI计算食物热量及营养成分
        :param food_list: 食物列表，格式如[{"name": "食物名", "weight": 重量克}, ...]
        :return: 结构化计算结果
        """
        if not food_list:
            return {"error": "食物列表为空"}

        # 1. 构造提示词（明确计算逻辑和输出格式）
        prompt = self._build_prompt(food_list)

        # 2. 调用OpenAI API
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # 降低随机性，确保计算准确
                max_tokens=1000,
                response_format={"type": "json_object"}  # 强制返回JSON
            )

            # 3. 解析结果并打印
            return self._process_response(response)

        except Exception as e:
            return {"error": f"API调用失败：{str(e)}"}

    def _build_prompt(self, food_list: list) -> str:
        """构建提示词，说明计算规则"""
        # 格式化食物列表为自然语言
        food_text = "\n".join([f"- {item['name']}：{item['weight']}克" for item in food_list])

        return f"""
        请根据以下食物名称和重量，计算每种食物的营养成分及总汇总。

        食物列表：
        {food_text}

        计算规则：
        1. 基于每100克食物的营养数据（参考USDA标准），根据实际重量换算（如150克=1.5×100克数据）。
        2. 必算指标（单位：热量=千卡kcal，蛋白质/碳水/脂肪=克g）：
           - 热量：总能量
           - 蛋白质：总蛋白质含量
           - 碳水化合物：总碳水（含糖和纤维，但统一合并计算）
           - 脂肪：总脂肪含量
        3. 若食物有常见烹饪方式（如“油炸”“水煮”），需按烹饪后的数据计算（如油炸会增加脂肪）。
        4. 输出格式为JSON，包含：
           - foods：数组，每个元素含name（食物名）、weight（重量）、calories、protein、carbs、fat
           - total：对象，含总热量、总蛋白质、总碳水、总脂肪

        输出示例：
        {{
            "foods": [
                {{"name": "鸡胸肉", "weight": 150, "calories": 247.5, "protein": 34.5, "carbs": 0.0, "fat": 5.4}},
                ...
            ],
            "total": {{"total_calories": 500.0, "total_protein": 40.0, "total_carbs": 60.0, "total_fat": 10.0}}
        }}
        """

    def _process_response(self, response):
        """处理API响应，打印结果并返回结构化数据"""
        try:
            content = response.choices[0].message.content.strip()
            result = json.loads(content)

            # 打印到控制台
            print("\n" + "=" * 60)
            print(f"【计算时间】{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("【食物营养计算结果】")
            for food in result["foods"]:
                print(f"- {food['name']}（{food['weight']}g）：")
                print(
                    f"  热量：{food['calories']}kcal | 蛋白质：{food['protein']}g | 碳水：{food['carbs']}g | 脂肪：{food['fat']}g")
            print("\n【总计】")
            print(f"总热量：{result['total']['total_calories']}kcal | 总蛋白质：{result['total']['total_protein']}g")
            print(f"总碳水：{result['total']['total_carbs']}g | 总脂肪：{result['total']['total_fat']}g")
            print("=" * 60 + "\n")

            return {"success": True, "data": result}

        except json.JSONDecodeError:
            return {"error": "AI返回非JSON格式", "raw_content": content}
        except KeyError as e:
            return {"error": f"结果缺失字段：{str(e)}", "raw_content": content}
        except Exception as e:
            return {"error": f"结果处理失败：{str(e)}", "raw_content": content}