import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, r2_score, silhouette_score
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor

from backend.agents.state import AgentState

def ml_engineer_node(state: AgentState) -> AgentState:
    """
    The ML Engineer Agent trains multiple models and picks the best one.
    """
    print("--- ML ENGINEER AGENT THINKING ---")
    
    metadata = state.get("dataset_metadata", {})
    base_path = metadata.get("saved_path", "test_dataset.csv")
    engineered_path = base_path.replace(".csv", "_engineered.csv")
    
    try:
        df = pd.read_csv(engineered_path)
    except Exception:
        return {"models_evaluated": [{"error": "Engineered dataset not found."}], "best_model": None}

    target = state.get("target_column")
    task_type = state.get("task_type", "classification").lower()
    
    # 1. Define models based on task type
    models_to_try = {}
    metrics = []
    best_model_name = None
    best_model_obj = None
    best_score = -float('inf')

    if task_type == "clustering":
        # For clustering, there is no target column
        X = df.copy()
        if target and target in X.columns:
            X = X.drop(columns=[target])
            
        if len(X) < 5:
            return {"models_evaluated": [{"error": "Dataset too small to cluster."}], "best_model": None}
            
        models_to_try = {
            "KMeans": KMeans(n_clusters=3, random_state=42, n_init='auto'),
            "DBSCAN": DBSCAN(eps=0.5, min_samples=2),
            "Hierarchical": AgglomerativeClustering(n_clusters=3)
        }
        
        for name, model in models_to_try.items():
            try:
                # Clustering doesn't use train/test split in the same way
                labels = model.fit_predict(X)
                
                # Silhouette score requires at least 2 distinct clusters
                if len(set(labels)) > 1 and len(set(labels)) < len(X):
                    score = silhouette_score(X, labels)
                else:
                    score = -1.0 # Invalid clustering (e.g. everything is noise in DBSCAN)
                    
                metrics.append({"model": name, "silhouette_score": round(score, 4)})
                
                if score > best_score:
                    best_score = score
                    best_model_name = name
                    best_model_obj = model
            except Exception as e:
                print(f"[ML ENGINEER ERROR] Model {name} failed: {e}")
                metrics.append({"model": name, "error": str(e)})

    else:
        # Supervised Learning (Classification / Regression)
        if target not in df.columns:
            return {"models_evaluated": [{"error": f"Target column '{target}' not found."}], "best_model": None}
            
        X = df.drop(columns=[target])
        y = df[target]
        
        if len(df) < 5:
            return {"models_evaluated": [{"error": "Dataset too small to train."}], "best_model": None}
            
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        if task_type == "classification":
            models_to_try = {
                "Logistic Regression": LogisticRegression(max_iter=1000),
                "Random Forest": RandomForestClassifier(random_state=42),
                "XGBoost": XGBClassifier(random_state=42, eval_metric="logloss"),
                "LightGBM": LGBMClassifier(random_state=42)
            }
        elif task_type == "regression":
            models_to_try = {
                "Linear Regression": LinearRegression(),
                "Random Forest Regressor": RandomForestRegressor(random_state=42),
                "XGBoost Regressor": XGBRegressor(random_state=42),
                "LightGBM Regressor": LGBMRegressor(random_state=42)
            }

        for name, model in models_to_try.items():
            try:
                model.fit(X_train, y_train)
                preds = model.predict(X_test)
                
                if task_type == "classification":
                    acc = accuracy_score(y_test, preds)
                    score = acc
                    metrics.append({"model": name, "accuracy": round(acc, 4)})
                else:
                    r2 = r2_score(y_test, preds)
                    score = r2
                    metrics.append({"model": name, "r2_score": round(r2, 4)})
                    
                if score > best_score:
                    best_score = score
                    best_model_name = name
                    best_model_obj = model
            except Exception as e:
                print(f"[ML ENGINEER ERROR] Model {name} failed: {e}")
                metrics.append({"model": name, "error": str(e)})
                
    # 3. Save the best model
    saved_model_path = None
    if best_model_obj is not None:
        models_dir = "./models"
        os.makedirs(models_dir, exist_ok=True)
        file_prefix = os.path.splitext(os.path.basename(base_path))[0]
        saved_model_path = os.path.join(models_dir, f"{file_prefix}_best_model.pkl")
        joblib.dump(best_model_obj, saved_model_path)
        print(f"Best model ({best_model_name}) saved to {saved_model_path}")
        
    return {
        "models_evaluated": metrics,
        "best_model": best_model_name
    }
