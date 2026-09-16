from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import relationship
import datetime

from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    projects = relationship("Project", back_populates="owner")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    status = Column(String, default="Created")  # Created, Running, Completed, Failed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    dataset_path = Column(String, nullable=True)
    data_quality_score = Column(Float, nullable=True)
    
    # Store the entire final leaderboard as JSON
    leaderboard = Column(JSON, nullable=True)
    best_model_name = Column(String, nullable=True)
    deployment_zip_path = Column(String, nullable=True)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="projects")
