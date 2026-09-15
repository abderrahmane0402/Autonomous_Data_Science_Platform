import os
import zipfile
from backend.agents.state import AgentState

def generate_api_code(features: list) -> str:
    """Generates the FastAPI python code for the specific model."""
    
    # We parse the feature list to create Pydantic model fields
    pydantic_fields = []
    for f in features:
        # Expected format from Data Engineer: "feature_name: action"
        parts = f.split(":")
        if len(parts) == 2:
            col = parts[0].strip()
            action = parts[1].strip()
            
            # Don't ask the user for columns that the model doesn't use!
            if action != "drop":
                # In a real app we'd map pandas dtypes to python types, but float is safe for ML
                pydantic_fields.append(f"    {col}: float")
        
    if not pydantic_fields:
        pydantic_fields.append("    feature_1: float  # Fallback")
        
    fields_str = "\n".join(pydantic_fields)
    
    return f"""from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI(title="ML Prediction API", version="1.0")

# Load the model on startup
try:
    model = joblib.load("model.pkl")
except Exception as e:
    model = None
    print(f"Error loading model: {{e}}")

class PredictionRequest(BaseModel):
{fields_str}

@app.get("/health")
def health_check():
    return {{"status": "ok", "model_loaded": model is not None}}

@app.post("/predict")
def predict(request: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
        
    # Convert request to DataFrame
    input_data = pd.DataFrame([request.model_dump()])
    
    try:
        prediction = model.predict(input_data)
        return {{"prediction": float(prediction[0])}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
"""

def generate_dockerfile() -> str:
    """Generates the Dockerfile for the API."""
    return """FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY deployment_api.py .
COPY model.pkl .

EXPOSE 8000

CMD ["uvicorn", "deployment_api:app", "--host", "0.0.0.0", "--port", "8000"]
"""

def deployment_node(state: AgentState) -> AgentState:
    """
    The Deployment Agent creates the API, Dockerfile, and zips them with the model.
    """
    print("--- DEPLOYMENT AGENT THINKING ---")
    
    metadata = state.get("dataset_metadata", {})
    base_path = metadata.get("saved_path", "test_dataset.csv")
    
    # Locate the trained model
    models_dir = "../models" if not base_path.startswith("test_") else "."
    model_path = os.path.join(models_dir, "tuned_best_model.pkl")
    if not os.path.exists(model_path):
        model_path = os.path.join(models_dir, "best_model.pkl")
        
    if not os.path.exists(model_path):
        print("Deployment Error: No trained model found to package.")
        return state

    # Get the features to build the API schema
    features = state.get("features_engineered", [])
    if not features:
        features = ["feature_1: pass"] # Fallback
        
    api_code = generate_api_code(features)
    dockerfile_code = generate_dockerfile()
    requirements_code = "fastapi\nuvicorn\npydantic\nscikit-learn\npandas\njoblib\nxgboost\nlightgbm\n"
    
    # Create the zip package
    deploy_dir = "../deployment" if not base_path.startswith("test_") else "."
    os.makedirs(deploy_dir, exist_ok=True)
    zip_path = os.path.join(deploy_dir, "deployment_package.zip")
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # Write files directly into the zip
        zipf.writestr("deployment_api.py", api_code)
        zipf.writestr("Dockerfile", dockerfile_code)
        zipf.writestr("requirements.txt", requirements_code)
        # Add the physical model file and rename it to 'model.pkl' inside the zip
        zipf.write(model_path, "model.pkl")
        
    print(f"Deployment Package successfully zipped to {zip_path}!")
    
    return state
