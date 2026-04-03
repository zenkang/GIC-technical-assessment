from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api.cafes import router as cafes_router
from app.api.employees import router as employees_router

app = FastAPI(
    title="Café Employee Manager API",
    description="RESTful API for managing cafes and employees",
    version="1.0.0",
)

# Allow the frontend (served via nginx on port 80) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded logos as static files at /static/logos/<filename>
os.makedirs("/app/static/logos", exist_ok=True)
app.mount("/static", StaticFiles(directory="/app/static"), name="static")

app.include_router(cafes_router)
app.include_router(employees_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
