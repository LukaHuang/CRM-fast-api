from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import engine, Base
from app.routers import customers_router, events_router, analytics_router, email_router
from app.services.scheduler_service import scheduler_service

# Create database tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時
    scheduler_service.start()
    yield
    # 關閉時
    scheduler_service.stop()


app = FastAPI(
    title="CRM API",
    description="Customer Relationship Management API for event and course data",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(customers_router)
app.include_router(events_router)
app.include_router(analytics_router)
app.include_router(email_router)

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def root():
    return FileResponse("app/static/index.html")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
