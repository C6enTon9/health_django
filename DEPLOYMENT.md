# Health Django 项目 Docker 部署完整指南

## 📋 项目简介

这是一个基于Django + Django REST Framework的健康管理系统，提供用户管理、健康信息记录、饮食计划、AI聊天等功能。

**技术栈：**
- Python 3.10
- Django 5.1.7
- Django REST Framework 3.16.0
- SQLite (可扩展为PostgreSQL/MySQL)
- OpenAI API (AI聊天功能)

**主要功能模块：**
- 用户认证与管理 (user)
- 健康信息管理 (information)
- 计划管理 (plan)
- AI聊天助手 (chat)
- 饮食管理 (diet)

## 🚀 快速部署（5分钟上线）

### 第一步：克隆项目代码

```bash
# 进入工作目录
cd ~

# 克隆代码仓库
git clone https://github.com/C6enTon9/health_django.git

# 进入项目目录
cd health_django
```

### 第二步：配置环境变量

**创建或编辑 .env 文件：**

```bash
# 方式1：直接编辑
vim .env

# 方式2：使用cat创建
cat > .env << 'EOF'
# Django 核心配置
DJANGO_SECRET_KEY=your-secure-secret-key-here-change-me-to-random-string
DEBUG=False
ALLOWED_HOSTS=*

# OpenAI API 配置
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_BASE_URL=https://api.gptsapi.net/v1
EOF
```

**📌 重要配置说明：**

| 配置项 | 说明 | 示例值 |
|--------|------|--------|
| `DJANGO_SECRET_KEY` | Django密钥，必须修改为随机字符串 | `django-insecure-xy12@abc...` |
| `DEBUG` | 调试模式，生产环境必须设为False | `False` |
| `ALLOWED_HOSTS` | 允许的主机，生产环境建议填写实际IP或域名 | `192.168.1.100,example.com` |
| `OPENAI_API_KEY` | OpenAI API密钥 | `sk-xxx...` |
| `OPENAI_BASE_URL` | API基础URL | `https://api.gptsapi.net/v1` |

**生成安全的SECRET_KEY：**

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 第三步：解决Docker权限问题（重要）

如果遇到 `URLSchemeUnknown: Not supported URL scheme http+docker` 错误：

```bash
# 1. 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 2. 添加当前用户到docker组
sudo usermod -aG docker $USER

# 3. 重新加载组权限
newgrp docker
# 或者退出SSH重新登录

# 4. 验证权限
docker ps
```

### 第四步：启动容器

**方式A：使用Docker Compose（推荐）**

```bash
# 构建并启动容器
docker-compose up -d --build

# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f web
```

**方式B：使用原生Docker命令**

```bash
# 1. 构建镜像
docker build -t health_django:latest .

# 2. 创建必要目录
mkdir -p temp_images staticfiles

# 3. 运行容器
docker run -d \
  --name health_django \
  -p 8088:8088 \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/db.sqlite3:/app/db.sqlite3 \
  -v $(pwd)/temp_images:/app/temp_images \
  -v $(pwd)/staticfiles:/app/staticfiles \
  health_django:latest

# 4. 查看容器状态
docker ps

# 5. 查看日志
docker logs -f health_django
```

### 第五步：验证部署

```bash
# 在服务器上测试
curl http://localhost:8088

# 或检查健康状态
curl http://localhost:8088/admin/
```

**从浏览器访问：**
```
http://服务器IP:8088
```

**访问API文档：**
```
http://服务器IP:8088/swagger/
http://服务器IP:8088/redoc/
```

## 📦 常用管理命令

### Docker Compose 命令

| 操作 | Docker Compose 命令 | 原生 Docker 命令 |
|------|---------------------|------------------|
| 启动容器 | `docker-compose up -d` | `docker start health_django` |
| 停止容器 | `docker-compose down` | `docker stop health_django` |
| 重启容器 | `docker-compose restart` | `docker restart health_django` |
| 查看日志 | `docker-compose logs -f web` | `docker logs -f health_django` |
| 查看状态 | `docker-compose ps` | `docker ps \| grep health_django` |
| 进入容器 | `docker-compose exec web bash` | `docker exec -it health_django bash` |
| 删除容器 | `docker-compose down` | `docker rm -f health_django` |

### Django 管理命令

**使用Docker Compose：**

```bash
# 数据库迁移
docker-compose exec web python manage.py migrate

# 创建超级用户
docker-compose exec web python manage.py createsuperuser

# 收集静态文件
docker-compose exec web python manage.py collectstatic --noinput

# 清理过期会话
docker-compose exec web python manage.py clearsessions

# 进入Django Shell
docker-compose exec web python manage.py shell
```

**使用原生Docker：**

```bash
# 数据库迁移
docker exec health_django python manage.py migrate

# 创建超级用户
docker exec -it health_django python manage.py createsuperuser

# 收集静态文件
docker exec health_django python manage.py collectstatic --noinput

# 进入Django Shell
docker exec -it health_django python manage.py shell
```

### 日志管理

```bash
# 查看实时日志（Docker Compose）
docker-compose logs -f web

# 查看最近100行日志
docker-compose logs --tail=100 web

# 查看实时日志（原生Docker）
docker logs -f health_django

# 查看最近100行日志
docker logs --tail=100 health_django

# 导出日志到文件
docker logs health_django > app.log 2>&1
```

### 更新代码并重新部署

**方式A：Docker Compose 更新**

```bash
# 1. 进入项目目录
cd ~/health_django

# 2. 拉取最新代码
git pull origin main

# 3. 停止旧容器
docker-compose down

# 4. 重新构建并启动
docker-compose up -d --build

# 5. 查看状态
docker-compose ps

# 6. 清理旧镜像（可选）
docker image prune -f
```

**方式B：原生Docker更新**

```bash
# 1. 进入项目目录
cd ~/health_django

# 2. 拉取最新代码
git pull origin main

# 3. 停止并删除旧容器
docker stop health_django
docker rm health_django

# 4. 重新构建镜像
docker build -t health_django:latest .

# 5. 启动新容器
docker run -d \
  --name health_django \
  -p 8088:8088 \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/db.sqlite3:/app/db.sqlite3 \
  -v $(pwd)/temp_images:/app/temp_images \
  -v $(pwd)/staticfiles:/app/staticfiles \
  health_django:latest

# 6. 查看状态
docker ps | grep health_django

# 7. 清理旧镜像（可选）
docker image prune -f
```

## 数据持久化

项目使用以下volume进行数据持久化：
- `./db.sqlite3` - 数据库文件
- `./temp_images` - 临时图片存储
- `./staticfiles` - 静态文件

## 防火墙配置

如果服务器开启了防火墙，需要开放8088端口：

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 8088/tcp

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=8088/tcp
sudo firewall-cmd --reload
```

## 生产环境建议

1. **使用反向代理**: 建议在容器前添加Nginx作为反向代理
2. **HTTPS配置**: 配置SSL证书，使用HTTPS访问
3. **数据库**: 考虑使用PostgreSQL或MySQL替代SQLite
4. **备份策略**: 定期备份`db.sqlite3`和`temp_images`目录
5. **日志管理**: 配置日志轮转和集中管理
6. **监控**: 添加健康检查和监控告警

## 故障排查

### 容器无法启动
```bash
# 查看详细日志
docker-compose logs web

# 检查端口占用
netstat -tuln | grep 8088
```

### 数据库迁移失败
```bash
# 手动执行迁移
docker-compose exec web python manage.py migrate --noinput
```

### 权限问题
```bash
# 修改文件权限
chmod 666 db.sqlite3
chmod -R 777 temp_images
```

## 快速部署脚本

创建一键部署脚本 `deploy.sh`：

```bash
#!/bin/bash
set -e

echo "开始部署 Health Django 项目..."

# 拉取最新代码
echo "1. 拉取最新代码..."
git pull origin main

# 停止旧容器
echo "2. 停止旧容器..."
docker-compose down

# 构建并启动新容器
echo "3. 构建并启动容器..."
docker-compose up -d --build

# 等待容器启动
echo "4. 等待容器启动..."
sleep 10

# 查看状态
echo "5. 检查容器状态..."
docker-compose ps

# 显示日志
echo "6. 显示最近日志..."
docker-compose logs --tail=50 web

echo "部署完成！访问 http://$(hostname -I | awk '{print $1}'):8088"
```

使用方法：
```bash
chmod +x deploy.sh
./deploy.sh
```
