from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class DatasetMetadata(BaseModel):
    filename: str
    file_size_bytes: int
    rows: int
    columns: int
    column_names: List[str]
    datatypes: Dict[str, str]
    missing_values: Dict[str, int]
    missing_values_percentage: float = 0.0
    quality_score: float = 1.0
    memory_usage_mb: float = 0.0
    pii_columns_detected: List[str]
    upload_date: datetime

class UploadResponse(BaseModel):
    message: str
    metadata: DatasetMetadata
    saved_path: str
