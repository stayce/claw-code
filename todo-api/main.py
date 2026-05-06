from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from db import create_db_and_tables
from routes.todos import router as todos_router
from routes.tags import router as tags_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Todo API",
    description="Personal task manager with OpenClaw skill integration",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(todos_router)
app.include_router(tags_router)


@app.get("/health")
def health():
    return JSONResponse({"ok": True, "message": "Todo API is running"})
