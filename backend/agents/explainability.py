import pandas as pd
import joblib
import shap
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend — safe for background threads
import matplotlib.pyplot as plt
import os
import numpy as np
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from backend.agents.state import AgentState

class ExplainabilityReport(BaseModel):
    explanation: str = Field(description="A 2-paragraph human-readable explanation of which features drive the model's predictions based on the SHAP values.")

def explainability_node(state: AgentState) -> AgentState:
    """
    The Explainability Agent uses SHAP to determine feature importance 
    and Qwen to write a business-friendly explanation.
    """
    print("--- EXPLAINABILITY AGENT THINKING ---")
    
    metadata = state.get("dataset_metadata", {})
    base_path = metadata.get("saved_path", "test_dataset.csv")
    engineered_path = base_path.replace(".csv", "_engineered.csv")
    models_dir = "./models" if not base_path.startswith("test_") else "."
    
    # Try to load the tuned model first, fallback to best_model
    file_prefix = os.path.splitext(os.path.basename(base_path))[0]
    model_path = os.path.join(models_dir, f"{file_prefix}_tuned_best_model.pkl")
    if not os.path.exists(model_path):
        model_path = os.path.join(models_dir, f"{file_prefix}_best_model.pkl")
        
    try:
        df = pd.read_csv(engineered_path)
        model = joblib.load(model_path)
    except Exception as e:
        print(f"Explainability Error: {e}")
        return state
        
    target = state.get("target_column")
    if target not in df.columns or state.get("task_type") == "clustering":
        return state
        
    X = df.drop(columns=[target])
    
    # Calculate SHAP values
    # For speed and compatibility, we use a sample if the dataset is large
    X_sample = shap.sample(X, 100) if len(X) > 100 else X
    
    try:
        explainer = shap.Explainer(model, X_sample)
        shap_values = explainer(X_sample)
        
        # Calculate mean absolute SHAP values for feature importance
        if len(shap_values.values.shape) == 3:
            # For multiclass classification, average over classes
            mean_shap = np.abs(shap_values.values).mean(axis=(0, 2))
        else:
            mean_shap = np.abs(shap_values.values).mean(axis=0)
            
        feature_importance = dict(zip(X.columns, mean_shap))
        
        # Sort features by importance
        sorted_features = sorted(feature_importance.items(), key=lambda item: item[1], reverse=True)
        top_features = {k: round(float(v), 4) for k, v in sorted_features[:5]}
        
        # Generate and save a SHAP bar plot
        reports_dir = "./reports" if not base_path.startswith("test_") else "."
        os.makedirs(reports_dir, exist_ok=True)
        plot_path = os.path.join(reports_dir, f"{file_prefix}_shap_summary.png")
        
        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X_sample, plot_type="bar", show=False)
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()
        
    except Exception as e:
        print(f"SHAP Explainer failed, falling back to native feature importances: {e}")
        try:
            # Fallback for models like LightGBM that break SHAP TreeExplainer
            import numpy as np
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1][:10]
            top_features = {X.columns[i]: float(importances[i]) for i in indices}
            
            # Create a simple bar chart instead
            plt.figure(figsize=(10, 6))
            plt.barh(list(top_features.keys())[::-1], list(top_features.values())[::-1], color='dodgerblue')
            plt.xlabel("Native Feature Importance")
            plt.title(f"Top 10 Feature Importances")
            plot_path = os.path.join("reports" if not base_path.startswith("test_") else ".", f"shap_summary.png")
            plt.savefig(plot_path, bbox_inches='tight')
            plt.close()
        except Exception as fallback_e:
            print(f"Explainability completely failed: {fallback_e}")
            return state

    # Use Qwen to explain the top features
    llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0.1)
    structured_llm = llm.with_structured_output(ExplainabilityReport)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI Explainability Expert. Review the top SHAP feature importances. Explain in simple, business-friendly language how the model makes its predictions and what the most important variables are."),
        ("human", "Task: {task}\nTarget: {target}\nTop Features (SHAP values):\n{features}\n\nWrite the explanation.")
    ])
    
    try:
        report: ExplainabilityReport = (prompt | structured_llm).invoke({
            "task": state.get("task_type"),
            "target": target,
            "features": top_features
        })
        explanation = report.explanation
    except Exception:
        explanation = "Failed to generate text explanation."
        
    print(f"Top Features: {top_features}")
    
    # Update state
    # We will just append this to the eda_results or create a new key.
    return {
        "explainability": {
            "top_features": top_features,
            "explanation": explanation,
            "plot_path": plot_path
        }
    }
