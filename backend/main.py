from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from backend.routers import datasets, agents, auth, projects
from backend.database import engine, Base
from backend import models_db

# Create the SQLite database tables automatically
Base.metadata.create_all(bind=engine)

from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Autonomous Data Science Platform",
    description="Multi-Agent AI System for Data Science Lifecycle",
    version="1.0.0"
)

# Ensure directories exist
os.makedirs("deployment", exist_ok=True)
os.makedirs("reports", exist_ok=True)

app.mount("/deployment", StaticFiles(directory="deployment"), name="deployment")
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(datasets.router)
app.include_router(agents.router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
