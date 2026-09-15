import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, r2_score
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from xgboost import XGBClassifier, XGBRegressor

from backend.agents.state import AgentState

def ml_engineer_node(state: AgentState) -> AgentState:
    """
    The ML Engineer Agent trains multiple models and picks the best one.
    """
    print("--- ML ENGINEER AGENT THINKING ---")
    
    metadata = state.get("dataset_metadata", {})
    # Load the cleaned, engineered dataset from the previous step
    base_path = metadata.get("saved_path", "test_dataset.csv")
    engineered_path = base_path.replace(".csv", "_engineered.csv")
    
    try:
        df = pd.read_csv(engineered_path)
    except Exception:
        return {"models_evaluated": [{"error": "Engineered dataset not found."}], "best_model": None}

    target = state.get("target_column")
    task_type = state.get("task_type", "classification").lower()
    
    if target not in df.columns:
        return {"models_evaluated": [{"error": f"Target column '{target}' not found."}], "best_model": None}
        
    # Split data
    X = df.drop(columns=[target])
    y = df[target]
    
    # Simple check for very small datasets (like our n=5 test)
    if len(df) < 5:
        return {"models_evaluated": [{"error": "Dataset too small to train."}], "best_model": None}
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    models_to_try = {}
    metrics = []
    best_model_name = None
    best_model_obj = None
    best_score = -float('inf')
    
    # 1. Define models based on task type
    if task_type == "classification":
        models_to_try = {
            "Logistic Regression": LogisticRegression(),
            "Random Forest": RandomForestClassifier(random_state=42),
            "XGBoost": XGBClassifier(random_state=42, eval_metric="logloss")
        }
    elif task_type == "regression":
        models_to_try = {
            "Linear Regression": LinearRegression(),
            "Random Forest Regressor": RandomForestRegressor(random_state=42),
            "XGBoost Regressor": XGBRegressor(random_state=42)
        }
    else:
         return {"models_evaluated": [{"error": "Unsupported task type."}], "best_model": None}

    # 2. Train and Evaluate
    for name, model in models_to_try.items():
        try:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            
            if task_type == "classification":
                acc = accuracy_score(y_test, preds)
                # Primary metric for classification: Accuracy
                score = acc
                metrics.append({
                    "model": name,
                    "accuracy": round(acc, 4)
                })
            else:
                r2 = r2_score(y_test, preds)
                # Primary metric for regression: R2 (Higher is better)
                score = r2
                metrics.append({
                    "model": name,
                    "r2_score": round(r2, 4)
                })
                
            # Keep track of the winner
            if score > best_score:
                best_score = score
                best_model_name = name
                best_model_obj = model
                
        except Exception as e:
            metrics.append({"model": name, "error": str(e)})
            
    # 3. Save the best model
    saved_model_path = None
    if best_model_obj is not None:
        models_dir = "../models" if not base_path.startswith("test_") else "."
        os.makedirs(models_dir, exist_ok=True)
        saved_model_path = os.path.join(models_dir, "best_model.pkl")
        joblib.dump(best_model_obj, saved_model_path)
        print(f"Best model ({best_model_name}) saved to {saved_model_path}")
        
    return {
        "models_evaluated": metrics,
        "best_model": best_model_name
    }
