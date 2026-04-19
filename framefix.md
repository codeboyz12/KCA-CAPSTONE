# FRAMEFIX: Backend Change Log (ภาษาไทย)

เอกสารนี้สรุปเฉพาะงานที่เพิ่ม/แก้ในฝั่ง Backend สำหรับระบบ Job Queue และ Worker ด้วย Celery
(ไม่มีการเปลี่ยน Business Logic ฝั่ง Frontend ในเอกสารนี้)

## เป้าหมายที่ทำ

- เพิ่มโหมดประมวลผลแบบงานพื้นหลัง (asynchronous) ให้ API ที่ใช้ ML
- แยกงานหนักไปทำใน Worker เพื่อลดการบล็อกที่ API
- เพิ่ม endpoint สำหรับตรวจสถานะงานจาก task_id
- คงการใช้งานแบบ synchronous เดิมไว้ เพื่อไม่ให้ API เดิมพัง

## สิ่งที่เพิ่มใหม่ (Backend)

### 1) โครง Celery

- เพิ่มไฟล์ตั้งค่า Celery app
- กำหนด Broker และ Result Backend ผ่าน Environment Variables
- ตั้ง serialization เป็น JSON

ไฟล์ที่เพิ่ม:
- backend/celery_app.py

### 2) งาน Worker (Tasks)

- เพิ่ม task สำหรับ predict
- เพิ่ม task สำหรับ recommend
- task จะเรียก service logic กลางแทนการเขียนซ้ำใน router

ไฟล์ที่เพิ่ม:
- backend/tasks/__init__.py
- backend/tasks/ml_tasks.py

### 3) แยก Service Logic กลาง

- ย้าย logic คำนวณ predict/recommend ออกจาก router มาไว้ใน service
- เพิ่ม ensure_models_loaded() เพื่อโหลดโมเดลและ prior เมื่อจำเป็น
- เพิ่มการ cache สถานะทรัพยากร ML ด้วย flag resources_loaded

ไฟล์ที่เพิ่ม:
- backend/ml/service.py

ไฟล์ที่แก้:
- backend/ml/state.py

### 4) API สำหรับเช็กสถานะงาน

- เพิ่ม endpoint GET /api/v1/jobs/{task_id}
- คืนสถานะงาน เช่น PENDING, STARTED, SUCCESS, FAILURE
- ถ้างานเสร็จจะคืน result ถ้างานล้มเหลวจะคืน error

ไฟล์ที่เพิ่ม:
- backend/routers/jobs.py

### 5) ปรับ Router เดิมให้รองรับ async_mode

- POST /api/v1/predict
  - ค่าเริ่มต้น: ทำงานแบบ sync
  - ถ้า async_mode=true: ส่งเข้า queue แล้วคืน task_id

- POST /api/v1/recommend
  - ค่าเริ่มต้น: ทำงานแบบ sync
  - ถ้า async_mode=true: ส่งเข้า queue แล้วคืน task_id

ไฟล์ที่แก้:
- backend/routers/predict.py
- backend/routers/recommend.py

### 6) ผูก router ใหม่เข้าระบบ FastAPI

ไฟล์ที่แก้:
- backend/main.py

### 7) ปรับ startup ให้ใช้ service loader กลาง

- ลดโค้ดโหลดโมเดลซ้ำใน lifespan

ไฟล์ที่แก้:
- backend/core/lifespan.py

### 8) เพิ่มค่า config และ dependencies ที่ต้องใช้

ไฟล์ที่แก้:
- backend/core/config.py
  - เพิ่ม CELERY_BROKER_URL
  - เพิ่ม CELERY_RESULT_BACKEND

- backend/requirements.txt
  - เพิ่ม celery
  - เพิ่ม redis

## การเปลี่ยนฝั่ง Infrastructure ที่เกี่ยวข้องกับ Backend

- เพิ่ม service Redis สำหรับ broker/result backend
- เพิ่ม service ml-worker สำหรับรัน Celery worker
- ปรับ ml-backend ให้ mount โฟลเดอร์ backend ทั้งก้อนเพื่อสะท้อนโค้ดแบบ dev

ไฟล์ที่แก้:
- docker-compose.yml

## สรุปผลลัพธ์ที่ได้

- API เดิมยังใช้งานได้ (sync)
- API รองรับการส่งงานเข้า queue ได้ (async)
- มี endpoint ตรวจสถานะงานจนได้ผลลัพธ์จริง
- โค้ด backend แยกชั้นชัดขึ้น (router -> service -> task)

## Endpoint ที่ใช้งานหลังแก้

- POST /api/v1/predict
- POST /api/v1/predict?async_mode=true
- POST /api/v1/recommend
- POST /api/v1/recommend?async_mode=true&top_k=6
- GET /api/v1/jobs/{task_id}

## หมายเหตุ

- ถ้าจะรันโหมด queue ต้องมี Redis และ Celery worker ทำงานอยู่
- ถ้าเครื่องยังไม่เปิด Docker Engine การรัน docker compose จะล้มเหลวทันที
