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
  - `daily_calories`: 每日推荐热量摄入(卡路里/天)，基于久坐活动水平(系数1.2)

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