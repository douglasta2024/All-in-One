import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routes.youtube_to_notion import router as yt_router
from services.notebooklm import ensure_notebooks

load_dotenv()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await asyncio.to_thread(ensure_notebooks)
    yield


app = FastAPI(title="All-in-One API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(yt_router, prefix="/api")
