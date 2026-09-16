from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import os
import shutil

from backend.models import UploadResponse, DatasetMetadata
from backend.models_db import Project
from backend.database import get_db
from backend.services.ingestion import load_dataset, scan_and_anonymize_pii, extract_metadata, UPLOAD_PROGRESS

router = APIRouter(prefix="/datasets", tags=["Datasets"])

UPLOAD_DIR = "datasets"
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB limit for testing

@router.get("/progress/{filename}")
def get_upload_progress(filename: str):
    return UPLOAD_PROGRESS.get(filename, {"status": "Waiting in queue...", "percent": 0})

@router.post("/upload", response_model=UploadResponse)
def upload_dataset(
    file: UploadFile = File(...), 
    redact_pii: bool = Form(False),
    project_id: int = Form(None),
    db: Session = Depends(get_db)
):
    # 1. Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ['.csv', '.xls', '.xlsx', '.parquet']:
        raise HTTPException(status_code=400, detail="Invalid file format. Use CSV, Excel, or Parquet.")
        
    # 2. Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 100MB.")

    # Generate a globally unique filename using UUID to prevent any possible collision
    import uuid
    safe_name = file.filename.replace(" ", "_")
    unique_filename = f"proj_{project_id}_{uuid.uuid4().hex[:8]}_{safe_name}" if project_id else f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_name}"
        
    # 3. Save original file temporarily
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 4. Load dataset
        df = load_dataset(file_path, file.filename)
        
        # 5. PII Detection & Anonymization
        if redact_pii:
            df, pii_cols = scan_and_anonymize_pii(df, file.filename)
        else:
            df, pii_cols = df, []
            UPLOAD_PROGRESS[file.filename] = {"status": "Bypassing PII redaction...", "percent": 90}
            
        # 6. Re-save the anonymized dataset (overwriting original)
        if ext == '.csv':
            df.to_csv(file_path, index=False)
        elif ext in ['.xls', '.xlsx']:
            df.to_excel(file_path, index=False)
        elif ext == '.parquet':
            df.to_parquet(file_path, index=False)
            
        # 7. Extract Metadata
        meta_dict = extract_metadata(df, unique_filename, file_size, pii_cols)
        meta_dict['upload_date'] = datetime.now()
        
        metadata = DatasetMetadata(**meta_dict)
        
        UPLOAD_PROGRESS[file.filename] = {"status": "Complete!", "percent": 100}
        
        # 8. Link dataset to project in DB
        if project_id:
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                # Delete old dataset file if it exists to save disk space
                if project.dataset_path:
                    old_path = project.dataset_path  # already full relative path
                    if os.path.exists(old_path) and old_path != file_path:
                        try:
                            os.remove(old_path)
                        except Exception as e:
                            print(f"Warning: Failed to delete old dataset {old_path}: {e}")
                            
                project.dataset_path = file_path  # store full relative path with datasets/ prefix
                project.data_quality_score = metadata.quality_score
                
                # Convert datetime to string so it's JSON serializable
                meta_dict_json = metadata.dict()
                if "upload_date" in meta_dict_json and meta_dict_json["upload_date"]:
                    meta_dict_json["upload_date"] = meta_dict_json["upload_date"].isoformat()
                
                meta_dict_json["saved_path"] = file_path  # persist for agent pipeline use
                    
                project.dataset_metadata = meta_dict_json
                db.commit()
        
        return UploadResponse(
            message="Dataset uploaded and processed successfully.",
            metadata=metadata,
            saved_path=file_path
        )
        
    except ValueError as ve:
        os.remove(file_path)
        print(f"UPLOAD VALUE ERROR: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"UPLOAD EXCEPTION: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.delete("/project/{project_id}")
def delete_project_dataset(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if project.dataset_path:
        old_path = project.dataset_path  # already full relative path
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception as e:
                print(f"Failed to delete dataset file: {e}")
                
        project.dataset_path = None
        db.commit()
        
    return {"message": "Dataset detached and deleted successfully"}
