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
    -- Unified 384-dim embedding: encodes name + main_category + category + goal + duration
    text_embedding vector(384)
);