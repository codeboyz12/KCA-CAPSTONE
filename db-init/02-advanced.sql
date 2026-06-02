-- =============================================================
-- Advanced DB Design — Migration 02
-- Applies on top of 01-init.sql
-- =============================================================

-- -------------------------------------------------------------
-- 1. AUDIT COLUMNS — know when rows were added and from where
-- -------------------------------------------------------------
ALTER TABLE projects
    ADD COLUMN IF NOT EXISTS created_at  TIMESTAMPTZ DEFAULT now(),
    ADD COLUMN IF NOT EXISTS source      VARCHAR(20) DEFAULT 'historical';
-- source values: 'historical' | 'sample' | 'user_submission'

-- -------------------------------------------------------------
-- 2. CONSTRAINTS — enforce data integrity
-- -------------------------------------------------------------
ALTER TABLE projects
    ADD CONSTRAINT chk_goal_positive    CHECK (goal_usd > 0),
    ADD CONSTRAINT chk_duration_positive CHECK (duration_days > 0),
    ADD CONSTRAINT chk_state_binary     CHECK (state_binary IN (0, 1));

ALTER TABLE projects
    ALTER COLUMN name          SET NOT NULL,
    ALTER COLUMN category      SET NOT NULL,
    ALTER COLUMN goal_usd      SET NOT NULL,
    ALTER COLUMN duration_days SET NOT NULL,
    ALTER COLUMN state_binary  SET NOT NULL;

-- -------------------------------------------------------------
-- 3. NORMALIZATION — categories lookup table
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    category_id   SERIAL PRIMARY KEY,
    name          VARCHAR(100) UNIQUE NOT NULL,
    main_category VARCHAR(100),
    created_at    TIMESTAMPTZ DEFAULT now()
);

-- Populate from existing data
INSERT INTO categories (name)
SELECT DISTINCT category FROM projects
ON CONFLICT (name) DO NOTHING;

-- Add FK from projects to categories
ALTER TABLE projects
    ADD COLUMN IF NOT EXISTS category_id INT;

UPDATE projects p
SET category_id = c.category_id
FROM categories c
WHERE p.category = c.name;

ALTER TABLE projects
    ADD CONSTRAINT fk_category
    FOREIGN KEY (category_id) REFERENCES categories (category_id);

-- -------------------------------------------------------------
-- 4. INDEXES — query performance
-- -------------------------------------------------------------

-- B-tree indexes for filter / sort queries
CREATE INDEX IF NOT EXISTS idx_projects_category
    ON projects (category);

CREATE INDEX IF NOT EXISTS idx_projects_state
    ON projects (state_binary);

CREATE INDEX IF NOT EXISTS idx_projects_category_state
    ON projects (category, state_binary);

CREATE INDEX IF NOT EXISTS idx_projects_created_at
    ON projects (created_at DESC);

-- HNSW vector index — replaces full table scan on every recommend call
-- m=16, ef_construction=64 is a good default for 300k rows
CREATE INDEX IF NOT EXISTS idx_projects_text_embedding_hnsw
    ON projects USING hnsw (text_embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS idx_projects_struct_embedding_hnsw
    ON projects USING hnsw (struct_embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- -------------------------------------------------------------
-- 5. MATERIALIZED VIEW — category statistics
--    Used by the retrain pipeline instead of computing on the fly
-- -------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS category_stats AS
SELECT
    category,
    COUNT(*)                          AS total_projects,
    SUM(state_binary)                 AS successful_count,
    ROUND(AVG(state_binary)::NUMERIC, 4)  AS success_rate,
    ROUND(AVG(goal_usd)::NUMERIC, 2)      AS avg_goal_usd,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY goal_usd)::NUMERIC, 2)
                                      AS median_goal_usd,
    ROUND(AVG(duration_days)::NUMERIC, 1) AS avg_duration_days
FROM projects
GROUP BY category;

CREATE UNIQUE INDEX IF NOT EXISTS idx_category_stats_category
    ON category_stats (category);

-- Refresh with: REFRESH MATERIALIZED VIEW CONCURRENTLY category_stats;

-- -------------------------------------------------------------
-- 6. PREDICTION LOG — store every inference request
--    Feeds MLOps drift monitoring
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS prediction_log (
    log_id          BIGSERIAL PRIMARY KEY,
    requested_at    TIMESTAMPTZ DEFAULT now(),
    category        VARCHAR(100),
    goal_usd        FLOAT,
    duration_days   INT,
    prob_success    FLOAT,
    is_viable       BOOLEAN,
    model_version   VARCHAR(50) DEFAULT 'production',
    source          VARCHAR(20) DEFAULT 'api'   -- 'api' | 'celery'
);

CREATE INDEX IF NOT EXISTS idx_prediction_log_requested_at
    ON prediction_log (requested_at DESC);

CREATE INDEX IF NOT EXISTS idx_prediction_log_category
    ON prediction_log (category);
