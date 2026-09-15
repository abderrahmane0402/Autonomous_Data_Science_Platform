import pandas as pd
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import os
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder

from backend.agents.state import AgentState

class Transformation(BaseModel):
    column: str = Field(description="The name of the column in the dataset")
    action: str = Field(description="The action to perform: 'drop', 'impute_mean', 'impute_median', 'impute_mode', 'scale_standard', 'scale_minmax', 'encode_label', 'encode_onehot', 'pass'")
    reasoning: str = Field(description="Why this action is being taken")

class EngineerDecision(BaseModel):
    transformations: List[Transformation] = Field(description="A list of transformations to apply to the dataset columns.")

def apply_transformations(df: pd.DataFrame, transformations: List[Transformation]) -> tuple[pd.DataFrame, List[str]]:
    """Applies the LLM's requested transformations to the dataframe safely."""
    df_engineered = df.copy()
    features_engineered = []
    
    for t in transformations:
        col = t.column
        action = t.action
        
        if col not in df_engineered.columns:
            continue
            
        features_engineered.append(f"{col}: {action}")
            
        if action == "drop":
            df_engineered.drop(columns=[col], inplace=True)
            
        elif action == "impute_mean":
            df_engineered[col] = df_engineered[col].fillna(df_engineered[col].mean())
            
        elif action == "impute_median":
            df_engineered[col] = df_engineered[col].fillna(df_engineered[col].median())
            
        elif action == "impute_mode":
            df_engineered[col] = df_engineered[col].fillna(df_engineered[col].mode()[0])
            
        elif action == "scale_standard":
            scaler = StandardScaler()
            df_engineered[[col]] = scaler.fit_transform(df_engineered[[col]])
            
        elif action == "scale_minmax":
            scaler = MinMaxScaler()
            df_engineered[[col]] = scaler.fit_transform(df_engineered[[col]])
            
        elif action == "encode_label":
            le = LabelEncoder()
            # Handle NaNs before encoding
            df_engineered[col] = df_engineered[col].fillna("Missing")
            df_engineered[col] = le.fit_transform(df_engineered[col].astype(str))
            
        elif action == "encode_onehot":
            df_engineered = pd.get_dummies(df_engineered, columns=[col], drop_first=True)
            
    return df_engineered, features_engineered

def data_engineer_node(state: AgentState) -> AgentState:
    """
    The Data Engineer Agent determines feature engineering steps and applies them.
    """
    print("--- DATA ENGINEER AGENT THINKING ---")
    
    metadata = state.get("dataset_metadata", {})
    file_path = metadata.get("saved_path", "test_dataset.csv") 
    
    try:
        df = pd.read_csv(file_path)
    except Exception:
        return {"features_engineered": ["Error: Dataset not found."]}

    # Prepare context for the LLM
    stats = state.get("eda_results", {}).get("statistics", {})
    plan = state.get("execution_plan", [])
    target = state.get("target_column")
    
    llm = ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0.1,
        max_tokens=4096  # Increased token limit!
    )
    
    structured_llm = llm.with_structured_output(EngineerDecision)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an Expert Data Engineer. Based on the supervisor's execution plan and the analyst's statistics, decide exactly how to transform EVERY column in the dataset (except the target column). Output a structured list of actions: 'drop', 'impute_mean', 'impute_median', 'impute_mode', 'scale_standard', 'scale_minmax', 'encode_label', 'encode_onehot', or 'pass'."),
        ("human", "Columns & Stats:\n{stats}\n\nTarget Column: {target}\n\nSupervisor Plan:\n{plan}\n\nProvide the transformation strategy.")
    ])
    
    chain = prompt | structured_llm
    
    decision: EngineerDecision = chain.invoke({
        "stats": stats,
        "target": target,
        "plan": plan
    })
    
    # Actually execute the cleaning!
    df_clean, applied_features = apply_transformations(df, decision.transformations)
    
    # Save the cleaned dataset
    clean_path = file_path.replace(".csv", "_engineered.csv")
    df_clean.to_csv(clean_path, index=False)
    print(f"Engineered dataset saved to {clean_path}")
    
    return {"features_engineered": applied_features}
