from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend import database, models_db, schemas
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", response_model=schemas.ProjectResponse)
def create_project(
    project: schemas.ProjectCreate, 
    db: Session = Depends(database.get_db),
    current_user: models_db.User = Depends(get_current_user)
):
    new_project = models_db.Project(
        name=project.name,
        owner_id=current_user.id,
        status="Created"
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("", response_model=List[schemas.ProjectResponse])
def get_projects(
    db: Session = Depends(database.get_db),
    current_user: models_db.User = Depends(get_current_user)
):
    # Only return projects owned by the currently logged in user
    projects = db.query(models_db.Project).filter(models_db.Project.owner_id == current_user.id).all()
    return projects

@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(database.get_db),
    current_user: models_db.User = Depends(get_current_user)
):
    project = db.query(models_db.Project).filter(
        models_db.Project.id == project_id, 
        models_db.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return project

@router.get("/{project_id}/report")
def get_project_report(
    project_id: int,
    db: Session = Depends(database.get_db),
    current_user: models_db.User = Depends(get_current_user)
):
    project = db.query(models_db.Project).filter(
        models_db.Project.id == project_id, 
        models_db.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    import os
    # Default to global report path as per current logic
    # In a full production system, we'd store a distinct report per project
    metadata = project.dataset_path or "test_dataset.csv"
    reports_dir = "reports" if not metadata.startswith("test_") else "."
    
    file_prefix = os.path.splitext(os.path.basename(metadata))[0]
    report_path = os.path.join(reports_dir, f"{file_prefix}_final_report.md")

    if not os.path.exists(report_path):
        return {"markdown": "# Report not found\nRun the AI agents to generate a report."}

    with open(report_path, "r", encoding="utf-8") as f:
        markdown = f.read()

    return {"markdown": markdown}

@router.get("/{project_id}/download-deployment")
def download_deployment_zip(project_id: int, db: Session = Depends(database.get_db)):
    from fastapi.responses import FileResponse
    import os
    
    project = db.query(models_db.Project).filter(models_db.Project.id == project_id).first()
    if not project or not project.deployment_zip_path:
        raise HTTPException(status_code=404, detail="Deployment package not found")
        
    # project.deployment_zip_path looks like "deployment/proj_1_..._deployment_package.zip"
    zip_path = os.path.join(".", project.deployment_zip_path)
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="ZIP file physically missing from server disk")
        
    return FileResponse(zip_path, filename=os.path.basename(zip_path), media_type="application/zip")

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(database.get_db),
    current_user: models_db.User = Depends(get_current_user)
):
    import os
    project = db.query(models_db.Project).filter(
        models_db.Project.id == project_id, 
        models_db.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # 1. Delete Dataset
    if project.dataset_path:
        dataset_file = os.path.join("datasets", project.dataset_path)
        if os.path.exists(dataset_file):
            try:
                os.remove(dataset_file)
            except:
                pass
                
    # 2. Delete Deployment Zip
    if project.deployment_zip_path:
        zip_file = os.path.join("deployment_package", project.deployment_zip_path)
        if os.path.exists(zip_file):
            try:
                os.remove(zip_file)
            except:
                pass
                
    # 3. Delete Report
    metadata = project.dataset_path or "test_dataset.csv"
    if not metadata.startswith("test_"):
        file_prefix = os.path.splitext(os.path.basename(metadata))[0]
        report_path = os.path.join("reports", f"{file_prefix}_final_report.md")
        shap_path = os.path.join("reports", f"{file_prefix}_shap_summary.png")
        if os.path.exists(report_path):
            os.remove(report_path)
        if os.path.exists(shap_path):
            os.remove(shap_path)

    # 4. Delete DB Record
    db.delete(project)
    db.commit()
    
    return {"message": "Project and all associated files deleted successfully"}
