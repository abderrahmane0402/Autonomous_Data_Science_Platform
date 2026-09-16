from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
import datetime

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True

# --- Project Schemas ---
class ProjectBase(BaseModel):
    name: str

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    status: str
    created_at: datetime.datetime
    dataset_path: Optional[str] = None
    data_quality_score: Optional[float] = None
    dataset_metadata: Optional[Any] = None
    leaderboard: Optional[Any] = None
    best_model_name: Optional[str] = None
    deployment_zip_path: Optional[str] = None
    owner_id: int

    class Config:
        orm_mode = True
        from_attributes = True
