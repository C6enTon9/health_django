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

### 16. 获取用户所有信息(包含饮食建议)

- **接口地址**：`/api/information/all/`
- **请求方法**：POST
- **认证要求**：需要Token认证
- **请求头**：
```
Authorization: Token your_token_here
```
- **请求体格式**：
```json
{
    "days": 7
}
```
- **参数说明**：
  - `days`：分析最近多少天的饮食数据(可选,默认7天,取值范围1-30)

- **响应示例**：
```json
{
    "code": 200,
    "message": "获取用户信息成功",
    "data": {
        "username": "test_user",
        "height": 175.0,
        "weight": 70.0,
        "age": 25,
        "gender": "male",
        "gender_display": "男",
        "target": "减肥",
        "information": "我是一名程序员",
        "target_calories": 2000.0,
        "bmi": 22.86,
        "bmi_category": "正常",
        "bmr": 1663.75,
        "daily_calories": 1996.5,
        "diet_suggestion": "根据您最近7天的饮食记录分析:\n您的平均每日热量摄入为1850.5千卡,目标值为2000千卡。热量摄入低于目标149.5千卡(7.5%),建议适当增加营养摄入,避免过度节食。\n蛋白质平均摄入75.2g/天,推荐值为87.5g/天。蛋白质摄入不足,建议增加鸡胸肉、鱼类、豆制品等优质蛋白来源。\n碳水化合物平均摄入220.3g/天,推荐值为262.5g/天。碳水化合物摄入偏低,适量碳水是能量来源,建议合理摄入全谷物。\n脂肪平均摄入60.1g/天,推荐值为61.1g/天。脂肪摄入比例适中。\n建议规律吃早餐,早餐对新陈代谢和一天的精力都很重要。\n针对您的减脂目标:建议控制总热量摄入,增加蛋白质比例,适量运动,避免过度节食。\n\n保持健康的饮食习惯,祝您早日达成目标!"
    }
}
```
- **返回字段说明**：
  - `username`：用户名
  - `height`：身高(cm)
  - `weight`：体重(kg)
  - `age`：年龄
  - `gender`：性别代码（male/female）
  - `gender_display`：性别显示（男/女）
  - `target`：健康目标
  - `information`：个人信息描述
  - `target_calories`：每日目标热量(kcal)
  - `bmi`：身体质量指数
  - `bmi_category`：BMI分类（偏瘦/正常/偏胖/肥胖）
  - `bmr`：基础代谢率(kcal/天)
  - `daily_calories`：每日推荐热量(kcal/天)
  - `diet_suggestion`：个性化饮食建议(纯文本,如果没有足够的饮食记录则为null)

- **说明**：
  - 一次性获取用户的所有基本信息、健康指标和个性化饮食建议
  - 饮食建议基于用户最近N天的饮食记录和健康目标智能生成
  - 如果用户信息不存在,返回400错误
  - 如果没有足够的饮食记录,`diet_suggestion`字段将为null,但其他信息正常返回
  - **本接口已整合原 `/api/diet/suggestion/` 接口的功能**

## PLAN API（训练/饮食计划管理）

### 1. 创建或更新计划

- **接口地址**：`/api/plan/manage/`
- **请求方法**：POST
- **认证要求**：需要Token认证
- **请求头**：
```
Authorization: Token your_token_here
```

#### 创建新计划
- **请求体格式**：
```json
{
    "title": "晨跑",
    "description": "30分钟慢跑",
    "day_of_week": 1,
    "start_time": "07:00",
    "end_time": "07:30"
}
```
- **参数说明**：
  - `title`：计划标题(必填)
  - `description`：详细描述(可选)
  - `day_of_week`：星期几,1-7代表周一到周日(必填)
  - `start_time`：开始时间,格式HH:MM(必填)
  - `end_time`：结束时间,格式HH:MM(必填)

- **响应示例**：
```json
{
    "code": 201,
    "message": "成功创建了新计划 '晨跑'。",
    "data": {
        "created": 1,
        "id": 1
    }
}
```

#### 更新现有计划
- **请求体格式**：
```json
{
    "id": 1,
    "title": "晨跑改为晚跑",
    "start_time": "18:00",
    "end_time": "18:30"
}
```
- **参数说明**：
  - `id`：要更新的计划ID(必填)
  - 其他字段：要更新的字段(可选,只传需要修改的字段)

- **响应示例**：
```json
{
    "code": 200,
    "message": "计划更新成功。",
    "data": {
        "updated": 1
    }
}
```

### 2. 获取计划列表(支持查询所有历史数据)

- **接口地址**：`/api/plan/list/`
- **请求方法**：GET
- **认证要求**：需要Token认证
- **请求头**：
```
Authorization: Token your_token_here
```

#### 查询参数(所有参数都是可选的):
- `day_of_week`: 星期几(1-7),筛选指定星期的计划
- `created_after`: 创建时间起始(YYYY-MM-DD),查询此日期之后创建的计划
- `created_before`: 创建时间结束(YYYY-MM-DD),查询此日期之前创建的计划
- `limit`: 返回数量限制,用于分页
- `offset`: 分页偏移量,默认0

#### 使用示例:

**查询所有计划**:
```
GET /api/plan/list/
```

**查询周一的所有计划**:
```
GET /api/plan/list/?day_of_week=1
```

**分页查询(每页20条,第1页)**:
```
GET /api/plan/list/?limit=20&offset=0
```

**查询2025年1月的所有计划**:
```
GET /api/plan/list/?created_after=2025-01-01&created_before=2025-01-31
```

**组合查询(周一的计划,2025年的,每页10条)**:
```
GET /api/plan/list/?day_of_week=1&created_after=2025-01-01&limit=10&offset=0
```

- **响应示例**:
```json
{
    "code": 200,
    "message": "计划获取成功。",
    "data": {
        "plans": [
            {
                "id": 1,
                "title": "晨跑",
                "description": "30分钟慢跑",
                "day_of_week": 1,
                "start_time": "07:00",
                "end_time": "07:30",
                "is_completed": false,
                "created_at": "2025-01-15 10:30:00",
                "updated_at": "2025-01-15 10:30:00"
            },
            {
                "id": 2,
                "title": "健康早餐",
                "description": "燕麦+鸡蛋+牛奶",
                "day_of_week": 1,
                "start_time": "08:00",
                "end_time": "08:30",
                "is_completed": true,
                "created_at": "2025-01-10 09:00:00",
                "updated_at": "2025-01-16 08:35:00"
            }
        ],
        "count": 2,
        "total": 25,
        "offset": 0,
        "limit": null
    }
}
```

- **返回字段说明**:
  - `plans`: 计划数组
  - `count`: 本次返回的计划数量
  - `total`: 符合条件的总计划数量
  - `offset`: 当前偏移量
  - `limit`: 当前限制数量(null表示返回所有)
  - `created_at`: 计划创建时间
  - `updated_at`: 计划最后更新时间

- **说明**:
  - **默认不限制时间范围**,可以查询所有历史数据
  - 结果按创建时间倒序排序(最新的在前)
  - 支持灵活的组合查询和分页
  - 适用于查看和管理所有训练/饮食计划

### 3. 删除单个计划

- **接口地址**：`/api/plan/manage/`
- **请求方法**：POST
- **认证要求**：需要Token认证
- **请求头**：
```
Authorization: Token your_token_here
```
- **请求体格式**：
```json
{
    "action": "delete",
    "plan_id": 1
}
```
- **参数说明**：
  - `action`：固定为"delete"
  - `plan_id`：要删除的计划ID

- **响应示例**：
```json
{
    "code": 200,
    "message": "ID为 1 的计划已成功删除。",
    "data": {
        "deleted": 1
    }
}
```

### 4. 批量删除计划

- **接口地址**：`/api/plan/manage/`
- **请求方法**：POST
- **认证要求**：需要Token认证
- **请求头**：
```
Authorization: Token your_token_here
```
- **请求体格式**：
```json
{
    "action": "delete_all",
    "day_of_week": 1
}
```
- **参数说明**：
  - `action`：固定为"delete_all"
  - `day_of_week`：星期几(可选,不传则删除所有计划)

- **响应示例**：
```json
{
    "code": 200,
    "message": "成功清空了星期 1 的 3 条计划。",
    "data": {
        "deleted": 3
    }
}
```

### 5. 批量创建计划

- **接口地址**：`/api/plan/manage/`
- **请求方法**：POST
- **认证要求**：需要Token认证
- **请求头**：
```
Authorization: Token your_token_here
```
- **请求体格式**：
```json
{
    "action": "bulk_create",
    "plans_data": [
        {
            "title": "周一晨跑",
            "description": "30分钟",
            "day_of_week": 1,
            "start_time": "07:00",
            "end_time": "07:30"
        },
        {
            "title": "周二游泳",
            "day_of_week": 2,
            "start_time": "18:00",
            "end_time": "19:00"
        }
    ]
}
```
- **参数说明**：
  - `action`：固定为"bulk_create"
  - `plans_data`：计划数组,每个计划包含title、day_of_week、start_time、end_time等字段

- **响应示例**：
```json
{
    "code": 201,
    "message": "成功为您批量创建了 2 条新计划。",
    "data": {
        "created": 2
    }
}
```

**说明**：
- Plan表同时用于训练计划和饮食计划,通过title和description区分
- 计划按星期几(day_of_week)循环,每周重复
- 所有计划都按day_of_week和start_time排序
- is_completed字段标记计划是否完成

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

### 6. 获取饮食建议 (已废弃，请使用 `/api/information/all/`)

> **注意**: 此接口已被整合到 `/api/information/all/` 接口中。建议使用新接口一次性获取所有用户信息和饮食建议。

- **接口地址**：`/api/diet/suggestion/` (已废弃)
- **请求方法**：POST
- **认证要求**：需要Token认证
- **请求头**：
```
Authorization: Token your_token_here
```
- **请求体格式**：
```json
{
    "days": 7
}
```
- **参数说明**：
  - `days`：分析最近多少天的数据，可选，默认7天，取值范围1-30

- **响应示例**：
```json
{
    "code": 200,
    "message": "生成饮食建议成功",
    "data": {
        "suggestion": "根据您最近7天的饮食记录分析:\n您的平均每日热量摄入为1850.5千卡,目标值为2000千卡。热量摄入低于目标149.5千卡(7.5%),建议适当增加营养摄入,避免过度节食。\n蛋白质平均摄入75.2g/天,推荐值为87.5g/天。蛋白质摄入不足,建议增加鸡胸肉、鱼类、豆制品等优质蛋白来源。\n碳水化合物平均摄入220.3g/天,推荐值为262.5g/天。碳水化合物摄入偏低,适量碳水是能量来源,建议合理摄入全谷物。\n脂肪平均摄入60.1g/天,推荐值为61.1g/天。脂肪摄入比例适中。\n建议规律吃早餐,早餐对新陈代谢和一天的精力都很重要。\n针对您的减脂目标:建议控制总热量摄入,增加蛋白质比例,适量运动,避免过度节食。\n\n保持健康的饮食习惯,祝您早日达成目标!"
    }
}
```

- **说明**：
  - **此接口已废弃，请使用 `/api/information/all/` 接口代替**
  - 根据用户最近N天的饮食记录和健康信息，智能生成个性化饮食建议
  - 返回一整段文字建议，包含：
    - 热量摄入分析和建议
    - 蛋白质摄入分析和建议
    - 碳水化合物摄入分析和建议
    - 脂肪摄入分析和建议
    - 餐次习惯建议(如早餐提醒)
    - 基于用户健康目标的个性化建议
  - 如果没有足够的饮食记录或未设置健康信息，会返回相应的错误提示

