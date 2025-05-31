## 后端

# 鸿蒙前端地址

https://github.com/guo-gy/HarmonyHealth

# 部署教程

### 1. 克隆项目

```bash
git clone https://github.com/guo-gy/health-django.git
cd health-django
```

### 2. 创建虚拟环境并安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置环境变量

根据你的实际情况，创建 `.env` 文件或修改 `settings.py`，配置数据库等信息。

### 4. 数据库迁移

```bash
python manage.py migrate
```

### 5. 创建超级用户（可选）

```bash
python manage.py createsuperuser
```

### 6. 运行后端

```bash
run.bat
```