from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.agents.state import AgentState
from backend.agents.supervisor import supervisor_agent_node
from backend.agents.analyst import data_analyst_node
from backend.agents.engineer import data_engineer_node
from backend.agents.ml_engineer import ml_engineer_node
from backend.agents.optimizer import optimizer_node
from backend.agents.explainability import explainability_node
from backend.agents.report import report_node
from backend.agents.deployment import deployment_node
from backend import database, models_db

router = APIRouter(prefix="/agents", tags=["Agents"])

class SupervisorRequest(BaseModel):
    dataset_metadata: Dict[str, Any]

class AgentPipelineRequest(BaseModel):
    dataset_metadata: Dict[str, Any]
    project_id: Optional[int] = None

@router.post("/test-supervisor")
async def test_supervisor(request: SupervisorRequest):
    """
    Test endpoint to pass metadata directly to the Supervisor Agent
    and see its decision.
    """
    try:
        # Initialize the state
        initial_state: AgentState = {
            "dataset_metadata": request.dataset_metadata,
            "task_type": None,
            "target_column": None,
            "execution_plan": [],
            "eda_results": {},
            "features_engineered": [],
            "requires_human_approval": True,
            "human_feedback": None,
            "models_evaluated": [],
            "best_model": None
        }
        
        # Run the supervisor node
        new_state = supervisor_agent_node(initial_state)
        return {
            "task_type": new_state["task_type"],
            "target_column": new_state["target_column"],
            "execution_plan": new_state["execution_plan"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-analyst")
async def test_analyst(request: SupervisorRequest):
    """
    Test endpoint to run the Supervisor AND the Analyst to see the flow.
    """
    try:
        initial_state: AgentState = {
            "dataset_metadata": request.dataset_metadata,
            "task_type": None,
            "target_column": None,
            "execution_plan": [],
            "eda_results": {},
            "features_engineered": [],
            "requires_human_approval": True,
            "human_feedback": None,
            "models_evaluated": [],
            "best_model": None
        }
        
        # 1. Run Supervisor
        state_after_supervisor = supervisor_agent_node(initial_state)
        # Merge state
        current_state = {**initial_state, **state_after_supervisor}
        
        # 2. Run Analyst
        state_after_analyst = data_analyst_node(current_state)
        current_state.update(state_after_analyst)
        
        return {
            "task_type": current_state["task_type"],
            "target_column": current_state["target_column"],
            "eda_summary": current_state["eda_results"]["markdown_summary"],
            "data_quality_score": current_state["eda_results"]["data_quality_score"],
            "statistics": current_state["eda_results"]["statistics"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-engineer")
async def test_engineer(request: SupervisorRequest):
    """
    Test endpoint to run Supervisor -> Analyst -> Engineer.
    """
    try:
        initial_state: AgentState = {
            "dataset_metadata": request.dataset_metadata,
            "task_type": None,
            "target_column": None,
            "execution_plan": [],
            "eda_results": {},
            "features_engineered": [],
            "requires_human_approval": True,
            "human_feedback": None,
            "models_evaluated": [],
            "best_model": None
        }
        
        # 1. Supervisor
        state1 = supervisor_agent_node(initial_state)
        current_state = {**initial_state, **state1}
        
        # 2. Analyst
        state2 = data_analyst_node(current_state)
        current_state.update(state2)
        
        # 3. Engineer
        state3 = data_engineer_node(current_state)
        current_state.update(state3)
        
        return {
            "target_column": current_state["target_column"],
            "features_engineered": current_state["features_engineered"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def run_full_pipeline_background(request: AgentPipelineRequest, project_id: int):
    db = database.SessionLocal()
    project = None
    if project_id:
        project = db.query(models_db.Project).filter(models_db.Project.id == project_id).first()

    try:
        actual_metadata = request.dataset_metadata.get("metadata", {})
        actual_metadata["saved_path"] = request.dataset_metadata.get("saved_path")
        
        initial_state: AgentState = {
            "dataset_metadata": actual_metadata,
            "task_type": None,
            "target_column": None,
            "execution_plan": [],
            "eda_results": {},
            "features_engineered": [],
            "requires_human_approval": True,
            "human_feedback": None,
            "models_evaluated": [],
            "best_model": None
        }
        
        # 1. Supervisor
        if project: project.status = "Running: Supervisor"; db.commit()
        state1 = supervisor_agent_node(initial_state)
        current_state = {**initial_state, **state1}
        
        # 2. Analyst
        if project: project.status = "Running: Analyst"; db.commit()
        state2 = data_analyst_node(current_state)
        current_state.update(state2)
        
        # 3. Engineer
        if project: project.status = "Running: Engineer"; db.commit()
        state3 = data_engineer_node(current_state)
        current_state.update(state3)
        
        # 4. ML Engineer
        if project: project.status = "Running: ML Engineer"; db.commit()
        state4 = ml_engineer_node(current_state)
        current_state.update(state4)
        
        # 5. Optimizer
        if project: project.status = "Running: Optimizer"; db.commit()
        state5 = optimizer_node(current_state)
        current_state.update(state5)
        
        # 6. Explainability
        if project: project.status = "Running: Explainability"; db.commit()
        state6 = explainability_node(current_state)
        current_state.update(state6)
        
        # 7. Report Agent
        if project: project.status = "Running: Report"; db.commit()
        report_node(current_state)
        
        # 8. Deployment Agent
        if project: project.status = "Running: Deployment"; db.commit()
        deployment_node(current_state)
        
        # 9. Save to Database!
        if project:
            project.status = "Completed"
            project.dataset_path = actual_metadata.get("saved_path")
            project.data_quality_score = actual_metadata.get("quality_score", 0.0)
            
            # Serialize leaderboard correctly
            leaderboard_json = [
                {
                    "model": m.get("model", ""),
                    "score": m.get("score") or m.get("accuracy") or m.get("r2_score") or m.get("silhouette_score") or 0.0,
                    "mae": m.get("mae"),
                    "mse": m.get("mse")
                } 
                for m in current_state.get("models_evaluated", [])
            ]
            project.leaderboard = leaderboard_json
            project.best_model_name = current_state.get("best_model")
            
            base_path = actual_metadata.get("saved_path", "test_dataset.csv")
            import os
            file_prefix = os.path.splitext(os.path.basename(base_path))[0]
            project.deployment_zip_path = f"deployment/{file_prefix}_deployment_package.zip"
            db.commit()

    except Exception as e:
        if project:
            project.status = f"Failed: {str(e)}"
            db.commit()
        print(f"Pipeline Failed: {e}")
    finally:
        db.close()


@router.post("/test-ml-engineer")
def test_ml_engineer(request: AgentPipelineRequest, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    """
    Test endpoint to run the FULL AI PIPELINE (Supervisor -> Analyst -> Engineer -> ML Engineer) in the background.
    """
    if request.project_id:
        project = db.query(models_db.Project).filter(models_db.Project.id == request.project_id).first()
        if project:
            project.status = "Running: Initialization"
            db.commit()

    background_tasks.add_task(run_full_pipeline_background, request, request.project_id)
    return {"message": "Pipeline started in background"}
