"""
Insert synthetic campaign samples into the projects table.

Usage:
    python scripts/add_samples.py --n 200
    python scripts/add_samples.py --n 500 --host localhost --port 5432
"""
import argparse
import random
import uuid
import psycopg2
from psycopg2.extras import execute_values

CATEGORIES = [
    "technology", "games", "film & video", "music", "art",
    "publishing", "food", "fashion", "theater", "comics",
    "photography", "crafts", "design", "dance", "journalism",
]

SUCCESS_RATE = {
    "technology": 0.20, "games": 0.35, "film & video": 0.37,
    "music": 0.47, "art": 0.41, "publishing": 0.31, "food": 0.25,
    "fashion": 0.24, "theater": 0.60, "comics": 0.54,
    "photography": 0.38, "crafts": 0.31, "design": 0.35,
    "dance": 0.63, "journalism": 0.21,
}


def generate_sample(category: str) -> tuple:
    goal_usd     = round(random.lognormvariate(9.5, 1.8), 2)
    duration_days = random.randint(7, 60)
    state_binary  = 1 if random.random() < SUCCESS_RATE.get(category, 0.35) else 0
    project_id   = str(uuid.uuid4())
    name         = f"Sample {category.title()} Project {project_id[:8]}"
    return (project_id, name, category, goal_usd, duration_days, state_binary, "sample")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n",    type=int, default=200, help="Number of samples to insert")
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=5432)
    parser.add_argument("--db",   type=str, default="kca_database")
    parser.add_argument("--user", type=str, default="kca_admin")
    parser.add_argument("--password", type=str, default="secretpassword")
    args = parser.parse_args()

    conn = psycopg2.connect(
        dbname=args.db, user=args.user, password=args.password,
        host=args.host, port=args.port,
    )
    cur = conn.cursor()

    samples = [
        generate_sample(random.choice(CATEGORIES))
        for _ in range(args.n)
    ]

    execute_values(
        cur,
        """
        INSERT INTO projects (project_id, name, category, goal_usd, duration_days, state_binary, source)
        VALUES %s
        ON CONFLICT (project_id) DO NOTHING;
        """,
        samples,
    )
    # refresh materialized view so category_stats stays current
    cur.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY category_stats;")
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM projects;")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()

    print(f"Inserted {args.n} new samples.")
    print(f"Total rows in projects table: {total}")


if __name__ == "__main__":
    main()
