from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import psycopg2
import warnings
warnings.filterwarnings('ignore')

# 1. สร้าง Instance ของแอปพลิเคชัน
app = FastAPI(title="KCA ML Engine API", version="1.0.0")

# 2. ตั้งค่า CORS (สำคัญมาก! เพื่อให้ Frontend React/Next.js เรียก API ได้โดยไม่ติด Error)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # ตอนขึ้น Production ค่อยเปลี่ยนเป็น URL ของ Frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading Models and Data into memory...")
try:
    clf_model = joblib.load("models/kca_classifier.pkl")
    reg_model = joblib.load("models/kca_regressor.pkl")
    encoder = joblib.load("models/category_encoder.pkl")
    scaler = joblib.load("models/structural_scaler.pkl")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    # ดึงค่า Prior (Success Rate เฉลี่ยของแต่ละหมวด) เก็บไว้ใน Memory เพื่อความรวดเร็ว
    conn = psycopg2.connect("dbname=kca_database user=kca_admin password=secretpassword host=db port=5432")
    cur = conn.cursor()
    cur.execute("SELECT category, AVG(state_binary) FROM projects GROUP BY category;")
    category_prior = {row[0]: float(row[1]) for row in cur.fetchall()}
    cur.close()
    conn.close()

    print("Models loaded successfully! (Data is handled by PostgreSQL)")
except Exception as e:
    print(f"Error during startup: {e}")

class CampaignInput(BaseModel):
    category: str
    goal_usd: float
    duration_days: int
    launch_month: int

# ==========================================
# API ENDPOINTS
# ==========================================

@app.get("/health")
def health_check():
    """Route สำหรับให้ Docker หรือ Load Balancer เช็คว่า Service ยังไม่ตาย"""
    return {"status": "ok", "service": "KCA ML Engine"}

def get_db_connection():
    return psycopg2.connect("dbname=kca_database user=kca_admin password=secretpassword host=db port=5432")

@app.get("/api/v1/metadata")
def get_metadata():
    """Route สำหรับให้ Frontend ดึงรายชื่อ Category ไปสร้าง Dropdown Menu"""
    # ดึงคลาสทั้งหมดที่ Encoder รู้จัก
    categories = encoder.classes_.tolist()
    return {"available_categories": categories}

@app.post("/api/v1/predict")
def predict_campaign(data: CampaignInput):
    """Route หลักสำหรับการ Inference (XGBoost + SHAP)"""
    try:
        # 1. เตรียมข้อมูล (Preprocessing)
        cat_enc = encoder.transform([data.category])[0]
        input_df = pd.DataFrame([[
            cat_enc, data.goal_usd, data.duration_days, data.launch_month
        ]], columns=['category_encoded', 'goal_usd', 'duration_days', 'launch_month'])

        # 2. ทำนายผล (Predict)
        prob_success = float(clf_model.predict_proba(input_df)[0][1])
        expected_pledged = float(reg_model.predict(input_df)[0])

        # 3. อธิบายผล (SHAP) - คอมเมนต์ไว้ชั่วคราวจนกว่าจะโหลด TreeExplainer ด้านบน
        # shap_values = explainer.shap_values(input_df)
        # top_factors = ... (เขียน logic ดึง Top 3 ปัจจัยบวก/ลบ)

        # 4. ส่งคำตอบกลับไปให้ Frontend
        return {
            "success": True,
            "prediction": {
                "probability_percentage": round(prob_success * 100, 2),
                "expected_pledged_usd": round(expected_pledged, 2),
                "is_viable": prob_success > 0.5
            },
            # "explanation": top_factors
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ==========================================
# API ENDPOINT: RECOMMENDATION ENGINE
# ==========================================

@app.post("/api/v1/recommend")
def get_similar_projects(data: CampaignInput, top_k: int = 3):
    """
    Route ดึงโปรเจกต์กรณีศึกษา โดยให้ PostgreSQL (pgvector) ช่วยค้นหา
    """
    try:
        # 1. สร้าง Vector ของ User
        user_text = f"A {data.category} project needing ${data.goal_usd} in {data.duration_days} days."
        user_text_emb = embedder.encode([user_text])[0].tolist()
        user_struct_emb = scaler.transform([[data.goal_usd, data.duration_days]])[0].tolist()
        
        # แปลงเป็น String รูปแบบที่ pgvector ต้องการ: '[0.1, 0.2, ...]'
        text_vec_str = '[' + ','.join(map(str, user_text_emb)) + ']'
        struct_vec_str = '[' + ','.join(map(str, user_struct_emb)) + ']'

        # 2. ค้นหาด้วย SQL Query (The Magic of pgvector)
        # เราดึง top 100 ที่คล้ายด้านข้อความมาก่อน แล้วค่อยมาจัดเรียงด้วยสมการอาจารย์
        query = """
            SELECT project_id, name, category, goal_usd, duration_days, state_binary,
                   (1 - (text_embedding <=> %s::vector)) AS text_sim,
                   (1 - (struct_embedding <=> %s::vector)) AS struct_sim
            FROM projects
            ORDER BY text_embedding <=> %s::vector
            LIMIT 100;
        """
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # ยิงคำสั่ง SQL โดยส่ง Vector ไปเทียบ
        cur.execute(query, (text_vec_str, struct_vec_str, text_vec_str))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # 3. นำ 100 โปรเจกต์ที่คล้ายสุด มาคำนวณ Composite Score แบบละเอียด
        W_TEXT, W_CAT, W_STRUCT, W_PRIOR = 0.3, 0.2, 0.3, 0.2
        scored_projects = []

        for row in rows:
            p_id, p_name, p_cat, p_goal, p_dur, p_state, text_sim, struct_sim = row
            
            cat_match = 1.0 if p_cat == data.category else 0.0
            prior_val = category_prior.get(p_cat, 0.0)
            
            # สมการของอาจารย์
            total_score = (W_TEXT * text_sim) + (W_CAT * cat_match) + \
                          (W_STRUCT * struct_sim) + (W_PRIOR * prior_val)
            
            scored_projects.append({
                "project_id": p_id,
                "name": p_name,
                "category": p_cat,
                "goal_usd": p_goal,
                "duration_days": p_dur,
                "state": "Successful" if p_state == 1 else "Failed",
                "similarity_score": round(total_score, 4)
            })

        # 4. เรียงลำดับจากคะแนนสูงสุด และส่งกลับแค่ top_k (เช่น 3 อันดับแรก)
        top_projects = sorted(scored_projects, key=lambda x: x["similarity_score"], reverse=True)[:top_k]

        return {
            "success": True,
            "target_category": data.category,
            "recommended_cases": top_projects
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# API ENDPOINT: BROWSE ALL PROJECTS (WITH PAGINATION)
# ==========================================

@app.get("/api/v1/projects")
def get_all_projects(page: int = 1, limit: int = 12):
    """
    Route สำหรับดึงข้อมูลโปรเจกต์ทั้งหมดเพื่อแสดงผลหน้าแรก (ทีละหน้า)
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 1. คำนวณ Offset (ข้ามไปกี่แถว)
        offset = (page - 1) * limit

        # 2. นับจำนวนโปรเจกต์ทั้งหมด (เพื่อเอาไปทำปุ่ม Page 1 of X ฝั่ง Frontend)
        cur.execute("SELECT COUNT(*) FROM projects;")
        total_items = cur.fetchone()[0]
        total_pages = (total_items + limit - 1) // limit

        # 3. ดึงข้อมูลแบบ Pagination (ไม่ดึง Vector มาด้วย เพื่อให้ API ทำงานไวที่สุด)
        query = """
            SELECT project_id, name, category, goal_usd, duration_days, state_binary
            FROM projects
            ORDER BY project_id
            LIMIT %s OFFSET %s;
        """
        cur.execute(query, (limit, offset))
        rows = cur.fetchall()
        
        cur.close()
        conn.close()

        # 4. จัดรูปแบบข้อมูล
        projects = []
        for row in rows:
            projects.append({
                "id": row[0],
                "name": row[1],
                "category": row[2],
                "goal": row[3],
                "duration": row[4],
                "state": "successful" if row[5] == 1 else "failed"
            })

        return {
            "success": True,
            "data": projects,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total_items,
                "limit": limit
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))