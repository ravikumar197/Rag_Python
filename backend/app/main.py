from pathlib import Path

from fastapi import FastAPI
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(
    BASE_DIR / ".env"
)


from app.api.routes import router


app = FastAPI()

app.include_router(router)