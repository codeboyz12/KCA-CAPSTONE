"""
Recompute text_embedding for every project using the unified sentence template:

    "{name}. A {main_category} Kickstarter project in the {category} subcategory,
     with a ${goal_usd:,.0f} funding goal and a {duration_days}-day campaign."

This collapses text_embedding and struct_embedding into one rich vector.
struct_embedding is dropped from the table at the end.

Steps performed:
  1. Build sentences from historical_knowledge_base.csv (+ main_category from notebook CSV)
  2. Encode with all-MiniLM-L6-v2 in batches of 512
  3. Save to backend/models/precomputed_text_embs_v2.npy
  4. Drop HNSW index on text_embedding
  5. UPDATE all rows in DB (batched execute_values)
  6. Recreate HNSW index
  7. DROP COLUMN struct_embedding

IMPORTANT: the build_sentence() function here must stay identical to the one
in backend/ml/service.py — both sides of the cosine similarity must use the
same template or scores become meaningless.
"""

import time
import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer

# ── CANONICAL template (keep in sync with backend/ml/service.py) ──────────────
def build_sentence(name: str, main_category: str, category: str,
                   goal_usd: float, duration_days: int) -> str:
    name_part = f"{name}. " if name and name.strip() else ""
    return (
        f"{name_part}A {main_category} Kickstarter project in the {category} subcategory, "
        f"with a ${goal_usd:,.0f} funding goal and a {duration_days}-day campaign."
    )
# ──────────────────────────────────────────────────────────────────────────────

print("=== Recomputing text_embedding with unified template ===\n")

# ── 1. Load knowledge base ────────────────────────────────────────────────────
print("Loading historical_knowledge_base.csv...")
df = pd.read_csv("backend/models/historical_knowledge_base.csv")
print(f"  {len(df):,} rows loaded.\n")

# ── 2. Enrich with main_category from the original notebook CSV ───────────────
main_cat_map: dict[str, str] = {}
try:
    orig = pd.read_csv(
        "notebook/final_data_capstone_new.csv",
        usecols=["id", "main_category"],
        dtype={"id": str},
    )
    main_cat_map = dict(zip(orig["id"], orig["main_category"]))
    print(f"  main_category loaded for {len(main_cat_map):,} projects.")
except Exception as exc:
    print(f"  Warning: could not load main_category ({exc}).")
    print("  Falling back to category for all rows.\n")

# ── 3. Build sentences ────────────────────────────────────────────────────────
print("Building sentences...")
sentences = []
for _, row in df.iterrows():
    pid       = str(row["project_id"])
    main_cat  = main_cat_map.get(pid, str(row["category"]))
    sentences.append(build_sentence(
        name          = str(row["name"]),
        main_category = main_cat,
        category      = str(row["category"]),
        goal_usd      = float(row["goal_usd"]),
        duration_days = int(row["duration_days"]),
    ))

print(f"  Example: {sentences[0]}\n")

# ── 4. Encode ─────────────────────────────────────────────────────────────────
print("Loading SentenceTransformer (all-MiniLM-L6-v2)...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print(f"Encoding {len(sentences):,} sentences (batch_size=512) — ~2-4 min on CPU...\n")
t0 = time.time()
embeddings = model.encode(
    sentences,
    batch_size=512,
    show_progress_bar=True,
    convert_to_numpy=True,
)
print(f"\n  Done in {time.time() - t0:.1f}s — shape: {embeddings.shape}\n")

# ── 5. Save .npy ──────────────────────────────────────────────────────────────
out_path = "backend/models/precomputed_text_embs_v2.npy"
np.save(out_path, embeddings)
print(f"Saved → {out_path}\n")

# ── 6. Connect to DB ──────────────────────────────────────────────────────────
print("Connecting to database...")
conn = psycopg2.connect(
    dbname="kca_database",
    user="kca_admin",
    password="secretpassword",
    host="localhost",
    port="5432",
)
cur = conn.cursor()
print("  Connected.\n")

# ── 7. Drop HNSW index before mass update (avoids incremental degradation) ────
print("Dropping HNSW index on text_embedding...")
cur.execute("DROP INDEX IF EXISTS idx_projects_text_embedding_hnsw;")
conn.commit()
print("  Done.\n")

# ── 8. UPDATE all rows in batches ─────────────────────────────────────────────
project_ids = df["project_id"].astype(str).tolist()
total       = len(project_ids)
batch_size  = 5_000

print(f"Updating {total:,} rows in DB (batch_size={batch_size:,})...")
t0 = time.time()

for i in range(0, total, batch_size):
    batch_ids  = project_ids[i : i + batch_size]
    batch_embs = embeddings[i : i + batch_size]

    data = [
        (pid, "[" + ",".join(f"{x:.6f}" for x in emb) + "]")
        for pid, emb in zip(batch_ids, batch_embs)
    ]

    execute_values(
        cur,
        """
        UPDATE projects AS p
        SET    text_embedding = v.emb::vector
        FROM   (VALUES %s) AS v(pid, emb)
        WHERE  p.project_id = v.pid
        """,
        data,
        page_size=batch_size,
    )
    conn.commit()

    done = min(i + batch_size, total)
    print(f"  {done:,}/{total:,}  ({done/total*100:.0f}%)")

print(f"  DB update done in {time.time() - t0:.1f}s\n")

# ── 9. Recreate HNSW index on updated vectors ─────────────────────────────────
print("Rebuilding HNSW index on text_embedding (m=16, ef_construction=64)...")
print("  This takes 2-5 min for 229k rows...")
t0 = time.time()
cur.execute("""
    CREATE INDEX idx_projects_text_embedding_hnsw
    ON  projects
    USING hnsw (text_embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
""")
conn.commit()
print(f"  Index built in {time.time() - t0:.1f}s\n")

# ── 10. Drop struct_embedding column ──────────────────────────────────────────
print("Dropping struct_embedding column...")
cur.execute("ALTER TABLE projects DROP COLUMN IF EXISTS struct_embedding;")
conn.commit()
print("  Done.\n")

cur.close()
conn.close()

print("✅  Migration complete.")
print(f"    New embeddings saved to: {out_path}")
print("    text_embedding — unified name + structure vector (384-dim)")
print("    struct_embedding — dropped")
