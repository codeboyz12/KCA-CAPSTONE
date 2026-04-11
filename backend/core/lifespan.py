from contextlib import asynccontextmanager
import joblib
from sentence_transformers import SentenceTransformer
from core.config import settings
from db.session import get_db_connection
from ml.state import ml
import warnings
warnings.filterwarnings("ignore")

@asynccontextmanager
async def lifespan(app):
    print("Loading models into memory...")
    try:
        ml.clf_model = joblib.load(settings.MODEL_CLASSIFIER)
        ml.reg_model = joblib.load(settings.MODEL_REGRESSOR)
        ml.encoder   = joblib.load(settings.MODEL_ENCODER)
        ml.scaler    = joblib.load(settings.MODEL_SCALER)
        ml.embedder  = SentenceTransformer(settings.SENTENCE_MODEL)

        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute("SELECT category, AVG(state_binary) FROM projects GROUP BY category;")
        ml.category_prior = {row[0]: float(row[1]) for row in cur.fetchall()}
        cur.close()
        conn.close()

        print("Models loaded successfully!")
    except Exception as e:
        print(f"Startup error: {e}")

    yield

    print("Shutting down...")