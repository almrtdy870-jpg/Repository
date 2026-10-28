FROM python:3.11-slim
WORKDIR /app

# تحديث وتثبيت أدوات النظام الضرورية
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# تثبيت المكتبات مباشرة وبدون الحاجة لملف خارجي
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir pyrogram tgcrypto

# نسخ باقي الملفات
COPY . .

CMD ["python", "main.py"]
