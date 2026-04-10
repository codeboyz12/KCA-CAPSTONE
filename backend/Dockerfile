# ใช้ Python 3.10 เวอร์ชันเล็ก (Slim) เพื่อลดขนาด Image
FROM python:3.10-slim

# กำหนดโฟลเดอร์ทำงานภายใน Container
WORKDIR /app

# ติดตั้ง libgomp1 ซึ่งจำเป็นสำหรับ XGBoost บน Linux
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

# ก๊อปปี้ไฟล์ requirements และติดตั้ง Library
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ก๊อปปี้โค้ดและโมเดลทั้งหมดเข้าไปใน Container
COPY . .

# เปิดพอร์ต 8000
EXPOSE 8000

# รัน FastAPI ด้วย Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]