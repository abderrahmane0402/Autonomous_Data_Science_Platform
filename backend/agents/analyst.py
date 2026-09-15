import pandas as pd
import numpy as np
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from backend.agents.state import AgentState

class AnalystReport(BaseModel):
    markdown_summary: str = Field(description="A professional, 2-3 paragraph markdown summary of the dataset's health, focusing on missing values, outliers, and interesting correlations.")
    data_quality_score: int = Field(description="A score from 1 to 100 representing the overall quality and cleanliness of the data.")

def calculate_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """Deterministically calculate statistics for the frontend."""
    stats = {
        "numerical": {},
        "categorical": {},
        "total_rows": len(df)
    }
    
    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        
        if pd.api.types.is_numeric_dtype(df[col]):
            stats["numerical"][col] = {
                "null_count": null_count,
                "mean": float(df[col].mean()) if not df[col].empty else 0.0,
                "median": float(df[col].median()) if not df[col].empty else 0.0,
                "std": float(df[col].std()) if not df[col].empty else 0.0,
                "min": float(df[col].min()) if not df[col].empty else 0.0,
                "max": float(df[col].max()) if not df[col].empty else 0.0,
            }
        else:
            value_counts = df[col].value_counts().head(5).to_dict()
            stats["categorical"][col] = {
                "null_count": null_count,
                "top_values": {str(k): int(v) for k, v in value_counts.items()},
                "unique_count": int(df[col].nunique())
            }
            
    return stats

def data_analyst_node(state: AgentState) -> AgentState:
    """
    The Data Analyst Agent calculates statistics and uses the LLM to write a summary.
    """
    print("--- DATA ANALYST AGENT THINKING ---")
    
    # Normally, we would load the dataset here using a path saved in the state.
    # For testing, we'll assume the dataframe is passed in or we use a dummy dataframe.
    # In a real workflow, the dataset path is in state['dataset_metadata']['saved_path']
    metadata = state.get("dataset_metadata", {})
    file_path = metadata.get("saved_path", "test_dataset.csv") 
    
    try:
        df = pd.read_csv(file_path)
    except Exception:
        # Fallback if file doesn't exist during pure testing
        df = pd.DataFrame()
        
    # 1. Calculate deterministic statistics
    if not df.empty:
        stats = calculate_statistics(df)
    else:
        stats = {"error": "Dataset could not be loaded."}
        
    # 2. Use Groq to analyze the statistics and write a report
    llm = ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0.2
    )
    
    structured_llm = llm.with_structured_output(AnalystReport)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an Expert Data Analyst. Review the provided statistical summary of a dataset. Write a brief markdown report highlighting data quality issues (missing values, weird distributions) and give it a quality score. Do not write code."),
        ("human", "Here are the dataset statistics:\n\n{stats}\n\nTarget column: {target}\nTask type: {task}\n\nWrite the report.")
    ])
    
    chain = prompt | structured_llm
    
    report: AnalystReport = chain.invoke({
        "stats": stats,
        "target": state.get("target_column", "Unknown"),
        "task": state.get("task_type", "Unknown")
    })
    
    print(f"Data Quality Score: {report.data_quality_score}/100")
    
    # 3. Update state
    eda_results = {
        "statistics": stats,
        "markdown_summary": report.markdown_summary,
        "data_quality_score": report.data_quality_score
    }
    
    return {"eda_results": eda_results}
