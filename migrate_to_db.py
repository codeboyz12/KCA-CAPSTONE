import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
import numpy as np
import time

print("=== 🚀 เริ่มกระบวนการย้ายข้อมูลเข้า PostgreSQL ===")

# 1. โหลดข้อมูลจากไฟล์
print("กำลังโหลดไฟล์ CSV และ NPY...")
try:
    df        = pd.read_csv('backend/models/historical_knowledge_base.csv')
    text_embs = np.load('backend/models/precomputed_text_embs_v2.npy')
    print(f"โหลดข้อมูลสำเร็จ: {len(df)} แถว")
except Exception as e:
    print(f"❌ หาไฟล์ไม่พบ กรุณาเช็ค Path: {e}")
    exit()

# 2. เชื่อมต่อ Database
print("กำลังเชื่อมต่อ Database...")
try:
    conn = psycopg2.connect(
        dbname="kca_database",
        user="kca_admin",
        password="secretpassword",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    print("เชื่อมต่อสำเร็จ!")
except Exception as e:
    print(f"❌ เชื่อมต่อ DB ไม่ได้: {e}")
    exit()

# 3. เตรียมข้อมูล
print("กำลังจัดเตรียมข้อมูล (Data Preparation)...")
data_to_insert = []
for i in range(len(df)):
    row          = df.iloc[i]
    text_vec_str = '[' + ','.join(map(str, text_embs[i])) + ']'
    data_to_insert.append((
        str(row['project_id']),
        str(row['name']),
        str(row['category']),
        float(row['goal_usd']),
        int(row['duration_days']),
        int(row['state_binary']),
        text_vec_str,
    ))

# 4. ยิงข้อมูลเข้า Database แบบ Batch
print("กำลังยิงข้อมูลเข้า Database (อาจใช้เวลา 1-3 นาทีขึ้นอยู่กับสเปคเครื่อง)...")
start_time = time.time()

cur.execute("TRUNCATE TABLE projects;")

insert_query = """
    INSERT INTO projects (project_id, name, category, goal_usd, duration_days, state_binary, text_embedding)
    VALUES %s
"""

execute_values(cur, insert_query, data_to_insert, page_size=5000)
conn.commit()

end_time = time.time()
print(f"✅ ย้ายข้อมูลเสร็จสมบูรณ์! ใช้เวลาไป {round(end_time - start_time, 2)} วินาที")

cur.close()
conn.close()
