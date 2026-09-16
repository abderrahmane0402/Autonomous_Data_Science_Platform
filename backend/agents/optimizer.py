import pandas as pd
import optuna
import mlflow
import mlflow.sklearn
import mlflow.xgboost
import mlflow.lightgbm
import joblib
import os
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor

from backend.agents.state import AgentState

# Configure Optuna to be less verbose
optuna.logging.set_verbosity(optuna.logging.WARNING)

def optimizer_node(state: AgentState) -> AgentState:
    """
    Takes the best model from the ML Engineer and uses Optuna to find the best hyperparameters.
    Logs everything to MLflow.
    """
    print("--- OPTIMIZER AGENT THINKING ---")
    
    best_model_name = state.get("best_model")
    task_type = state.get("task_type", "classification").lower()
    target = state.get("target_column")
    
    if not best_model_name or best_model_name == "None":
        return {"models_evaluated": state.get("models_evaluated", []) + [{"optimizer": "No best model provided."}]}
        
    metadata = state.get("dataset_metadata", {})
    base_path = metadata.get("saved_path", "test_dataset.csv")
    engineered_path = base_path.replace(".csv", "_engineered.csv")
    
    try:
        df = pd.read_csv(engineered_path)
    except Exception:
        return {"models_evaluated": state.get("models_evaluated", []) + [{"optimizer": "Engineered dataset not found."}]}
        
    if target not in df.columns or len(df) < 5 or task_type == "clustering":
        # Skip tuning for clustering or invalid datasets for now
        return {"models_evaluated": state.get("models_evaluated", []) + [{"optimizer": "Skipped tuning due to size or clustering."}]}
        
    X = df.drop(columns=[target])
    y = df[target]
    
    # We will use cross-validation instead of train_test_split for Optuna to be more robust
    
    def objective(trial):
        model = None
        
        if task_type == "classification":
            if best_model_name == "Logistic Regression":
                C = trial.suggest_float("C", 0.01, 10.0, log=True)
                model = LogisticRegression(C=C, max_iter=1000)
            elif best_model_name == "Random Forest":
                n_estimators = trial.suggest_int("n_estimators", 10, 100)
                max_depth = trial.suggest_int("max_depth", 2, 10)
                model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
            elif best_model_name == "XGBoost":
                learning_rate = trial.suggest_float("learning_rate", 0.01, 0.3, log=True)
                max_depth = trial.suggest_int("max_depth", 2, 8)
                model = XGBClassifier(learning_rate=learning_rate, max_depth=max_depth, random_state=42, eval_metric="logloss")
            elif best_model_name == "LightGBM":
                learning_rate = trial.suggest_float("learning_rate", 0.01, 0.3, log=True)
                num_leaves = trial.suggest_int("num_leaves", 20, 40)
                model = LGBMClassifier(learning_rate=learning_rate, num_leaves=num_leaves, random_state=42)
        else:
            if best_model_name == "Linear Regression":
                # Linear Regression doesn't have many hyperparameters to tune
                model = LinearRegression()
            elif best_model_name == "Random Forest Regressor":
                n_estimators = trial.suggest_int("n_estimators", 10, 100)
                max_depth = trial.suggest_int("max_depth", 2, 10)
                model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
            elif best_model_name == "XGBoost Regressor":
                learning_rate = trial.suggest_float("learning_rate", 0.01, 0.3, log=True)
                max_depth = trial.suggest_int("max_depth", 2, 8)
                model = XGBRegressor(learning_rate=learning_rate, max_depth=max_depth, random_state=42)
            elif best_model_name == "LightGBM Regressor":
                learning_rate = trial.suggest_float("learning_rate", 0.01, 0.3, log=True)
                num_leaves = trial.suggest_int("num_leaves", 20, 40)
                model = LGBMRegressor(learning_rate=learning_rate, num_leaves=num_leaves, random_state=42)
                
        if model is None:
            raise ValueError("Unsupported model for tuning")
            
        scoring = "accuracy" if task_type == "classification" else "r2"
        # Since our test dataset is tiny (n=5), we use cv=2. In production, use cv=5.
        cv_folds = 2 if len(df) < 10 else 5
        score = cross_val_score(model, X, y, cv=cv_folds, scoring=scoring).mean()
        return score

    # Create Optuna study
    direction = "maximize" # Maximize both Accuracy and R2
    study = optuna.create_study(direction=direction, study_name=f"{best_model_name}_optimization")
    
    # We restrict to 5 trials to keep it extremely fast for testing on your machine
    try:
        study.optimize(objective, n_trials=5, catch=(Exception,))
    except Exception as e:
        print(f"Optuna failed (usually due to tiny test dataset math errors): {e}")
        return state
        
    best_params = study.best_params
    best_tuned_score = study.best_value
    
    # Set up MLflow Tracking locally
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("Autonomous_DS_Platform")
    
    with mlflow.start_run(run_name=f"Tuned_{best_model_name}"):
        mlflow.log_params(best_params)
        mlflow.log_metric("cv_score", best_tuned_score)
        
        # Train the final tuned model on all data
        final_model = None
        if best_model_name == "Logistic Regression":
            final_model = LogisticRegression(**best_params, max_iter=1000)
        elif best_model_name == "Random Forest":
            final_model = RandomForestClassifier(**best_params, random_state=42)
        elif best_model_name == "XGBoost":
            final_model = XGBClassifier(**best_params, random_state=42, eval_metric="logloss")
        elif best_model_name == "LightGBM":
            final_model = LGBMClassifier(**best_params, random_state=42)
        elif best_model_name == "Linear Regression":
            final_model = LinearRegression()
        elif best_model_name == "Random Forest Regressor":
            final_model = RandomForestRegressor(**best_params, random_state=42)
        elif best_model_name == "XGBoost Regressor":
            final_model = XGBRegressor(**best_params, random_state=42)
        elif best_model_name == "LightGBM Regressor":
            final_model = LGBMRegressor(**best_params, random_state=42)
            
        if final_model:
            final_model.fit(X, y)
            
            if "XGBoost" in best_model_name:
                mlflow.xgboost.log_model(final_model, artifact_path="tuned_model")
            elif "LightGBM" in best_model_name:
                mlflow.lightgbm.log_model(final_model, artifact_path="tuned_model")
            else:
                mlflow.sklearn.log_model(final_model, artifact_path="tuned_model")
            
            # Save locally for the deployment agent later
            models_dir = "./models" if not base_path.startswith("test_") else "."
            os.makedirs(models_dir, exist_ok=True)
            file_prefix = os.path.splitext(os.path.basename(base_path))[0]
            saved_model_path = os.path.join(models_dir, f"{file_prefix}_tuned_best_model.pkl")
            joblib.dump(final_model, saved_model_path)
            
    print(f"Optuna found best params: {best_params} with Score: {best_tuned_score}")
    
    # Update the leaderboard with the tuned result
    leaderboard = state.get("models_evaluated", [])
    leaderboard.append({
        "model": f"TUNED {best_model_name}",
        "score": round(best_tuned_score, 4),
        "params": best_params
    })
    
    return {"models_evaluated": leaderboard}
