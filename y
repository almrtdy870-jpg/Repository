FROM python:3.11-slim
WORKDIR /app

# تحديث وتثبيت أدوات النظام الضرورية
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# تثبيت مكتبات البوت مباشرة وبدون الحاجة لملف خارجي
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir pyrogram tgcrypto

# نسخ باقي الملفات
COPY . .

CMD ["python", "main.py"]
