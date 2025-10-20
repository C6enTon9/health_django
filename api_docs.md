# HarmonyHealth API 文档
#### 都是post请求
**响应码说明**：
   - 200: 请求成功
   - 400: 业务逻辑错误
   - 300：数据错误

## USER API

### 1. 用户注册

- **接口地址**：`/api/user/register/`
- **请求体格式**：
```json
{
    "username": "用户ID",
    "password": "密码"
}
```

### 2. 用户登录

- **接口地址**：`/api/user/login/`
- **请求体格式**：
```json
{
    "username": "用户ID",
    "password": "密码"
}
```

## INFORMATION API

### 1. 更新身高

- **接口地址**：`/api/information/upd_height/`
- **请求体格式**：
```json
{
    "username": "用户ID",
    "height": "身高（单位：cm）"
}
```
- **响应示例**：
```json
{
    "code": 200,
    "message": "身高更新成功",
    "data": {
        "height": 175
    }
}
```

### 2. 获取身高

- **接口地址**：`/api/information/get_height/`
- **请求体格式**：
```json
{
    "username": "用户ID"
}
```

### 3. 更新体重

- **接口地址**：`/api/information/upd_weight/`
- **请求体格式**：
```json
{
    "username": "用户ID",
    "weight": "体重（单位：kg）"
}
```

### 4. 获取体重

- **接口地址**：`/api/information/get_weight/`
- **请求体格式**：
```json
{
    "username": "用户ID"
}
```

### 5. 更新年龄

- **接口地址**：`/api/information/upd_age/`
- **请求体格式**：
```json
{
    "username": "用户ID",
    "age": "年龄"
}
```

### 6. 获取年龄

- **接口地址**：`/api/information/get_age/`
- **请求体格式**：
```json
{
    "username": "用户ID"
}
```

### 7. 更新信息

- **接口地址**：`/api/information/upd_information/`
- **请求体格式**：
```json
{
    "username": "用户ID",
    "information": "用户信息"
}
```

### 8. 获取信息

- **接口地址**：`/api/information/get_information/`
- **请求体格式**：
```json
{
    "username": "用户ID"
}
```

### 9. 更新目标

- **接口地址**：`/api/information/upd_target/`
- **请求体格式**：
```json
{
    "username": "用户ID",
    "target": "用户目标"
}
```

### 10. 获取目标

- **接口地址**：`/api/information/get_target/`
- **请求体格式**：
```json
{
    "username": "用户ID"
}
```

### 11. 更新性别

- **接口地址**：`/api/information/update/gender/`
- **请求方法**：POST
- **认证要求**：需要Token认证
- **请求头**：
```
Authorization: Token your_token_here
```
- **请求体格式**：
```json
{
    "value": "male"  // 或 "female"
}
```
- **响应示例**：
```json
{
    "code": 200,
    "message": "信息更新成功",
    "data": {
        "gender": "male"
    }
}
```

### 12. 获取性别

- **接口地址**：`/api/information/get/gender/`
- **请求方法**：GET
- **认证要求**：需要Token认证
- **请求头**：
```
Authorization: Token your_token_here
```
- **响应示例**：
```json
{
    "code": 200,
    "message": "信息获取成功",
    "data": {
        "gender": "male"
    }
}
```

### 13. 获取健康指标（BMI、基础代谢率、每日推荐热量）

- **接口地址**：`/api/information/health-metrics/`
- **请求方法**：GET
- **认证要求**：需要Token认证
- **请求头**：
```
Authorization: Token your_token_here
```
- **响应示例**：
```json
{
    "code": 200,
    "message": "健康指标获取成功",
    "data": {
        "bmi": 22.86,
        "bmi_category": "正常",
        "bmr": 1543.75,
        "daily_calories": 1852.5,
        "height": 170.0,
        "weight": 66.0,
        "age": 25,
        "gender": "male"
    }
}
```
- **说明**：
  - `bmi`: 身体质量指数，公式：体重(kg) / 身高(m)²
  - `bmi_category`: BMI分类（偏瘦/正常/偏胖/肥胖）
  - `bmr`: 基础代谢率(卡路里/天)，使用Mifflin-St Jeor公式计算
  - `daily_calories`: 每日推荐热量摄入(卡路里/天)，如果用户设置了自定义目标热量则返回自定义值，否则基于久坐活动水平(系数1.2)计算

### 14. 更新每日目标热量

- **接口地址**：`/api/information/update/target_calories/`
- **请求方法**：POST
- **认证要求**：需要Token认证
- **请求头**：
```
Authorization: Token your_token_here
```
- **请求体格式**：
```json
{
    "value": 2000
}
```
- **参数说明**：
  - `value`：每日目标热量(kcal)，必填，数字类型
  - 设置为null可以清除自定义值，恢复使用系统计算值

- **响应示例**：
```json
{
    "code": 200,
    "message": "信息更新成功",
    "data": {
        "target_calories": 2000
    }
}
```
- **说明**：
  - 用户可以自定义每日目标热量，覆盖系统根据BMR计算的默认值
  - 设置后，`/api/information/health-metrics/`接口返回的`daily_calories`将使用此自定义值
  - 饮食管理模块会使用此值作为每日热量预算

### 15. 获取每日目标热量

- **接口地址**：`/api/information/get/target_calories/`
- **请求方法**：GET
- **认证要求**：需要Token认证
- **请求头**：
```
Authorization: Token your_token_here
```
- **响应示例**：
```json
{
    "code": 200,
    "message": "信息获取成功",
    "data": {
        "target_calories": 2000
    }
}
```
- **说明**：
  - 如果用户未设置自定义目标热量，返回值可能为null
  - 实际使用的每日热量值请通过`/api/information/health-metrics/`接口的`daily_calories`字段获取

## PLAN API

### 1. 获取计划

- **接口地址**：`/api/plan/get_plan/`
- **请求体格式**：
```json
{
    "username": "用户ID"
}
```

### 2. 更新计划

- **接口地址**：`/api/plan/upd_plan/`
- **请求体格式**：
```json
{
    "username": "用户ID",
    "new_info": "新的信息"//没有新信息则为空
}
```

## DIET API（饮食管理）

### 1. 获取所有食物列表

- **接口地址**：`/api/diet/foods/`
- **请求方法**：POST
- **认证要求**：需要Token认证
- **请求头**：
```
Authorization: Token your_token_here
```
- **请求体格式**：
```json
{}
```
- **响应示例**：
```json
{
    "code": 200,
    "message": "获取食物列表成功",
    "data": {
        "foods": [
            {
                "id": 1,
                "name": "米饭",
                "category": "主食",
                "calories": 116.0,
                "protein": 2.6,
                "carbohydrates": 25.9,
                "fat": 0.3
            },
            {
                "id": 2,
                "name": "鸡胸肉",
                "category": "肉类",
                "calories": 133.0,
                "protein": 19.4,
                "carbohydrates": 2.5,
                "fat": 5.0
            }
        ]
    }
}
```
- **说明**：
  - 返回数据库中所有食物信息
  - 营养成分均为每100g的含量
  - 食物按分类和名称排序

### 2. 添加食物到餐次

- **接口地址**：`/api/diet/add_food/`
- **请求方法**：POST
- **认证要求**：需要Token认证
- **请求头**：
```
Authorization: Token your_token_here
```
- **请求体格式**：
```json
{
    "meal_type": "breakfast",
    "food_id": 1,
    "weight": 200,
    "meal_date": "2025-10-16"
}
```
- **参数说明**：
  - `meal_type`：餐次类型，必填，可选值：`breakfast`(早餐)、`lunch`(午餐)、`dinner`(晚餐)
  - `food_id`：食物ID，必填
  - `weight`：重量(克)，必填
  - `meal_date`：日期(YYYY-MM-DD格式)，可选，默认为今天

- **响应示例**：
```json
{
    "code": 200,
    "message": "添加食物成功",
    "data": {
        "meal_food_id": 1,
        "food_name": "米饭",
        "weight": 200,
        "calories": 232.0
    }
}
```
- **说明**：
  - 会自动根据食物基础营养信息和重量计算该食物项的营养成分
  - 同一用户同一天的同一餐次可以添加多个食物
  - 返回的`meal_food_id`用于后续删除或更新操作

### 3. 从餐次删除食物

- **接口地址**：`/api/diet/remove_food/`
- **请求方法**：POST
- **认证要求**：需要Token认证
- **请求头**：
```
Authorization: Token your_token_here
```
- **请求体格式**：
```json
{
    "meal_food_id": 1
}
```
- **参数说明**：
  - `meal_food_id`：餐次食物项ID，必填（添加食物时返回的ID）

- **响应示例**：
```json
{
    "code": 200,
    "message": "删除食物成功",
    "data": null
}
```
- **说明**：
  - 删除后会自动重新计算该餐次的总热量
  - 只能删除属于当前用户的食物项

### 4. 更新食物重量

- **接口地址**：`/api/diet/update_weight/`
- **请求方法**：POST
- **认证要求**：需要Token认证
- **请求头**：
```
Authorization: Token your_token_here
```
- **请求体格式**：
```json
{
    "meal_food_id": 1,
    "weight": 300
}
```
- **参数说明**：
  - `meal_food_id`：餐次食物项ID，必填
  - `weight`：新的重量(克)，必填

- **响应示例**：
```json
{
    "code": 200,
    "message": "更新重量成功",
    "data": {
        "weight": 300,
        "calories": 348.0
    }
}
```
- **说明**：
  - 会自动重新计算该食物项的营养成分
  - 会自动更新该餐次的总热量
  - 只能更新属于当前用户的食物项

### 5. 获取每日餐次记录

- **接口地址**：`/api/diet/daily_meals/`
- **请求方法**：POST
- **认证要求**：需要Token认证
- **请求头**：
```
Authorization: Token your_token_here
```
- **请求体格式**：
```json
{
    "meal_date": "2025-10-16"
}
```
- **参数说明**：
  - `meal_date`：日期(YYYY-MM-DD格式)，可选，默认为今天

- **响应示例**：
```json
{
    "code": 200,
    "message": "获取每日餐次成功",
    "data": {
        "date": "2025-10-16",
        "meals": {
            "breakfast": {
                "foods": [
                    {
                        "meal_food_id": 1,
                        "food_id": 1,
                        "name": "米饭",
                        "weight": 200,
                        "calories": 232.0,
                        "protein": 5.2,
                        "carbohydrates": 51.8,
                        "fat": 0.6
                    },
                    {
                        "meal_food_id": 2,
                        "food_id": 6,
                        "name": "鸡胸肉",
                        "weight": 150,
                        "calories": 199.5,
                        "protein": 29.1,
                        "carbohydrates": 3.75,
                        "fat": 7.5
                    }
                ],
                "total_calories": 431.5,
                "total_protein": 34.3,
                "total_carbs": 55.55,
                "total_fat": 8.1
            },
            "lunch": {
                "foods": [],
                "total_calories": 0,
                "total_protein": 0,
                "total_carbs": 0,
                "total_fat": 0
            },
            "dinner": {
                "foods": [],
                "total_calories": 0,
                "total_protein": 0,
                "total_carbs": 0,
                "total_fat": 0
            }
        },
        "daily_total_calories": 431.5,
        "daily_total_protein": 34.3,
        "daily_total_carbs": 55.55,
        "daily_total_fat": 8.1,
        "recommended_protein": 81.3,
        "recommended_carbs": 243.3,
        "recommended_fat": 56.6
    }
}
```
- **说明**：
  - 返回指定日期的早中晚三餐数据
  - 如果某餐次没有记录，则`foods`为空数组，营养素总计为0
  - `daily_total_calories`：当日所有餐次的热量总和
  - `daily_total_protein`：当日所有餐次的蛋白质总和(g)
  - `daily_total_carbs`：当日所有餐次的碳水化合物总和(g)
  - `daily_total_fat`：当日所有餐次的脂肪总和(g)
  - `recommended_protein`：根据用户身体情况推荐的每日蛋白质摄入量(g)，按每日热量的17.5%计算
  - `recommended_carbs`：推荐的每日碳水化合物摄入量(g)，按每日热量的52.5%计算
  - `recommended_fat`：推荐的每日脂肪摄入量(g)，按每日热量的27.5%计算
  - 每个食物项包含完整的营养信息和唯一的`meal_food_id`
  - 如果用户未设置身体信息，推荐营养素字段将不会返回