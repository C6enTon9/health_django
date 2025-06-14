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