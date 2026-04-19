from contextlib import asynccontextmanager
from ml.service import ensure_models_loaded
import warnings
warnings.filterwarnings("ignore")

@asynccontextmanager
async def lifespan(app):
    print("Loading models into memory...")
    try:
        ensure_models_loaded()

        print("Models loaded successfully!")
    except Exception as e:
        print(f"Startup error: {e}")

    yield

    print("Shutting down...")