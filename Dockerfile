# 使用官方Python运行时作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=harmonyhealth_django.settings

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p /app/temp_images /app/staticfiles

# 收集静态文件
RUN python manage.py collectstatic --noinput || true

# 暴露端口
EXPOSE 8088

# 创建启动脚本
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Running database migrations..."\n\
python manage.py migrate --noinput\n\
echo "Starting Gunicorn server..."\n\
exec gunicorn harmonyhealth_django.wsgi:application \\\n\
    --bind 0.0.0.0:8088 \\\n\
    --workers 4 \\\n\
    --threads 2 \\\n\
    --timeout 60 \\\n\
    --access-logfile - \\\n\
    --error-logfile - \\\n\
    --log-level info\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# 运行启动脚本
CMD ["/app/entrypoint.sh"]
