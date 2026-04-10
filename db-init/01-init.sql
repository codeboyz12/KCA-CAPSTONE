-- เปิดใช้งาน Extension สำหรับระบบ AI Vector (ความคล้ายคลึง)
CREATE EXTENSION IF NOT EXISTS vector;

-- สร้างตาราง projects รอไว้เลย
CREATE TABLE IF NOT EXISTS projects (
    project_id VARCHAR(50) PRIMARY KEY,
    name TEXT,
    category VARCHAR(100),
    goal_usd FLOAT,
    duration_days INT,
    state_binary INT,
    -- คอลัมน์พิเศษสำหรับเก็บ Vector 384 มิติ (จาก SentenceTransformer)
    text_embedding vector(384),
    -- คอลัมน์สำหรับเก็บ Vector 2 มิติ (เป้าเงินและเวลาที่ Scale แล้ว)
    struct_embedding vector(2)
);