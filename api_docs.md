# HarmonyHealth API 文档

## USER API

### 1. 用户注册

- **接口地址**：`/api/user/register/`
- **请求方法**：`POST`
- **请求体格式**：
```json
{
    "user_id": "用户ID",
    "password": "密码"
}
```

### 2. 用户登录

- **接口地址**：`/api/user/login/`
- **请求方法**：`POST`
- **请求体格式**：
```json
{
    "user_id": "用户ID",
    "password": "密码"
}
```

## INFORMATION API

### 1. 更新身高

- **接口地址**：`/api/information/upd_height/`
- **请求方法**：`POST`
- **请求体格式**：
```json
{
    "user_id": "用户ID",
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
- **请求方法**：`POST`
- **请求体格式**：
```json
{
    "user_id": "用户ID"
}
```
- **响应示例**：
```json
{
    "code": 200,
    "message": "身高获取成功",
    "data": {
        "height": 175
    }
}
```

### 3. 更新体重

- **接口地址**：`/api/information/upd_weight/`
- **请求方法**：`POST`
- **请求体格式**：
```json
{
    "user_id": "用户ID",
    "weight": "体重（单位：kg）"
}
```
- **响应示例**：
```json
{
    "code": 200,
    "message": "体重更新成功",
    "data": {
        "weight": 70
    }
}
```

### 4. 获取体重

- **接口地址**：`/api/information/get_weight/`
- **请求方法**：`POST`
- **请求体格式**：
```json
{
    "user_id": "用户ID"
}
```
- **响应示例**：
```json
{
    "code": 200,
    "message": "体重获取成功",
    "data": {
        "weight": 70
    }
}
```

### 5. 更新年龄

- **接口地址**：`/api/information/upd_age/`
- **请求方法**：`POST`
- **请求体格式**：
```json
{
    "user_id": "用户ID",
    "age": "年龄"
}
```
- **响应示例**：
```json
{
    "code": 200,
    "message": "年龄更新成功",
    "data": {
        "age": 25
    }
}
```

### 6. 获取年龄

- **接口地址**：`/api/information/get_age/`
- **请求方法**：`POST`
- **请求体格式**：
```json
{
    "user_id": "用户ID"
}
```
- **响应示例**：
```json
{
    "code": 200,
    "message": "年龄获取成功",
    "data": {
        "age": 25
    }
}
```

### 7. 更新信息

- **接口地址**：`/api/information/upd_information/`
- **请求方法**：`POST`
- **请求体格式**：
```json
{
    "user_id": "用户ID",
    "information": "用户信息"
}
```
- **响应示例**：
```json
{
    "code": 200,
    "message": "信息更新成功",
    "data": {
        "information": "更新后的信息"
    }
}
```

### 8. 获取信息

- **接口地址**：`/api/information/get_information/`
- **请求方法**：`POST`
- **请求体格式**：
```json
{
    "user_id": "用户ID"
}
```
- **响应示例**：
```json
{
    "code": 200,
    "message": "信息获取成功",
    "data": {
        "information": "用户信息"
    }
}
```

### 9. 更新目标

- **接口地址**：`/api/information/upd_target/`
- **请求方法**：`POST`
- **请求体格式**：
```json
{
    "user_id": "用户ID",
    "target": "用户目标"
}
```
- **响应示例**：
```json
{
    "code": 200,
    "message": "目标更新成功",
    "data": {
        "target": "更新后的目标"
    }
}
```

### 10. 获取目标

- **接口地址**：`/api/information/get_target/`
- **请求方法**：`POST`
- **请求体格式**：
```json
{
    "user_id": "用户ID"
}
```
- **响应示例**：
```json
{
    "code": 200,
    "message": "目标获取成功",
    "data": {
        "target": "用户目标"
    }
}
```

## 通用说明

1. **响应码说明**：
   - 200: 请求成功
   - 400: 业务逻辑错误
   - 300：数据错误

2. **响应格式说明**：
   - code: 响应状态码
   - message: 响应消息
   - data: 响应数据