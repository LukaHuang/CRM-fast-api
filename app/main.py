from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import engine, Base
from app.routers import customers_router, events_router, analytics_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CRM API",
    description="Customer Relationship Management API for event and course data",
    version="1.0.0"
)

# Include routers
app.include_router(customers_router)
app.include_router(events_router)
app.include_router(analytics_router)

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def root():
    return FileResponse("app/static/index.html")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
