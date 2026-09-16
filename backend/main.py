from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from backend.routers import datasets, agents, auth
from backend.database import engine, Base
from backend import models_db

# Create the SQLite database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Autonomous Data Science Platform",
    description="Multi-Agent AI System for Data Science Lifecycle",
    version="1.0.0"
)

# Configure CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"], # Vite default is 5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(datasets.router)
app.include_router(agents.router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
