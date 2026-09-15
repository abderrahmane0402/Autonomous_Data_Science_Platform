from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from backend.agents.state import AgentState
from backend.agents.supervisor import supervisor_agent_node
from backend.agents.analyst import data_analyst_node
from backend.agents.engineer import data_engineer_node
from backend.agents.ml_engineer import ml_engineer_node
from backend.agents.optimizer import optimizer_node
from backend.agents.explainability import explainability_node

router = APIRouter(prefix="/agents", tags=["Agents"])

class SupervisorRequest(BaseModel):
    dataset_metadata: Dict[str, Any]

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

@router.post("/test-ml-engineer")
async def test_ml_engineer(request: SupervisorRequest):
    """
    Test endpoint to run the FULL AI PIPELINE (Supervisor -> Analyst -> Engineer -> ML Engineer).
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
        
        # 4. ML Engineer
        state4 = ml_engineer_node(current_state)
        current_state.update(state4)
        
        # 5. Optimizer (Phase 7)
        state5 = optimizer_node(current_state)
        current_state.update(state5)
        
        # 6. Explainability (Phase 8)
        state6 = explainability_node(current_state)
        current_state.update(state6)
        
        return {
            "task": current_state["task_type"],
            "target": current_state["target_column"],
            "best_model": current_state["best_model"],
            "explainability": current_state.get("explainability", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
