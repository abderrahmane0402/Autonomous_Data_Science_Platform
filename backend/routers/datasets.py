from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime
import os
import shutil

from backend.models import UploadResponse, DatasetMetadata
from backend.services.ingestion import load_dataset, scan_and_anonymize_pii, extract_metadata

router = APIRouter(prefix="/datasets", tags=["Datasets"])

UPLOAD_DIR = "../datasets"
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB limit for testing

@router.post("/upload", response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...)):
    # 1. Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ['.csv', '.xls', '.xlsx', '.parquet']:
        raise HTTPException(status_code=400, detail="Invalid file format. Use CSV, Excel, or Parquet.")
    
    # 2. Save file temporarily to disk to calculate size and read
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_size = os.path.getsize(file_path)
    
    # 3. Check size
    if file_size > MAX_FILE_SIZE:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 100MB.")
        
    try:
        # 4. Load dataset
        df = load_dataset(file_path, file.filename)
        
        # 5. PII Detection & Anonymization
        df, pii_cols = scan_and_anonymize_pii(df)
        
        # 6. Re-save the anonymized dataset (overwriting original)
        if ext == '.csv':
            df.to_csv(file_path, index=False)
        elif ext in ['.xls', '.xlsx']:
            df.to_excel(file_path, index=False)
        elif ext == '.parquet':
            df.to_parquet(file_path, index=False)
            
        # 7. Extract Metadata
        meta_dict = extract_metadata(df, file.filename, file_size, pii_cols)
        meta_dict['upload_date'] = datetime.now()
        
        metadata = DatasetMetadata(**meta_dict)
        
        return UploadResponse(
            message="Dataset uploaded and processed successfully.",
            metadata=metadata,
            saved_path=file_path
        )
        
    except ValueError as ve:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
