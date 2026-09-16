import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from backend.agents.state import AgentState

class FinalReport(BaseModel):
    markdown_content: str = Field(description="A comprehensive, beautifully formatted Markdown report combining all findings.")

def report_node(state: AgentState) -> AgentState:
    """
    The Report Agent compiles the entire state into a final Executive and Technical report.
    """
    print("--- REPORT AGENT THINKING ---")
    
    # 1. Gather all the context from the entire pipeline
    task = state.get("task_type", "Unknown")
    target = state.get("target_column", "Unknown")
    
    eda = state.get("eda_results", {})
    data_quality_score = eda.get("data_quality_score", "N/A")
    analyst_summary = eda.get("markdown_summary", "No summary provided.")
    
    features = state.get("features_engineered", [])
    
    leaderboard = state.get("models_evaluated", [])
    best_model = state.get("best_model", "None")
    
    explainability = state.get("explainability", {})
    shap_summary = explainability.get("explanation", "No explainability provided.")
    top_features = explainability.get("top_features", {})
    
    # 2. Ask Qwen to compile the final report
    llm = ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0.2,
        max_tokens=4096
    )
    
    from langchain_core.output_parsers import StrOutputParser
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Senior Data Science Consultant. Your job is to compile the notes from your engineering team into a cohesive, professional Final Report in Markdown format. The report should include: 1. Executive Summary 2. Data Quality & EDA 3. Engineering Methodology 4. Model Performance & Leaderboard 5. Explainability (Why the model makes decisions) 6. Conclusion."),
        ("human", "Task: {task}\nTarget: {target}\nData Quality Score: {score}\nAnalyst Notes: {analyst_summary}\nFeatures Engineered: {features}\nLeaderboard: {leaderboard}\nBest Model: {best_model}\nTop Drivers: {top_features}\nExplainability Notes: {shap_summary}\n\nWrite the final Markdown report.")
    ])
    
    try:
        final_markdown = (prompt | llm | StrOutputParser()).invoke({
            "task": task,
            "target": target,
            "score": data_quality_score,
            "analyst_summary": analyst_summary,
            "features": features,
            "leaderboard": leaderboard,
            "best_model": best_model,
            "top_features": top_features,
            "shap_summary": shap_summary
        })
        
        # Embed the SHAP image into the markdown report!
        plot_path = explainability.get("plot_path")
        if plot_path:
            # Get just the filename, not the full path, since it will be in the same folder
            img_name = os.path.basename(plot_path)
            final_markdown += f"\n\n## Feature Importance Chart\n![SHAP Feature Importance]({img_name})\n"
            
    except Exception as e:
        print(f"Report Generation Error: {e}")
        final_markdown = "# Error generating report\n" + str(e)
        
    # 3. Save the report to disk
    metadata = state.get("dataset_metadata", {})
    base_path = metadata.get("saved_path", "test_dataset.csv")
    
    reports_dir = "../reports" if not base_path.startswith("test_") else "."
    os.makedirs(reports_dir, exist_ok=True)
    
    report_path = os.path.join(reports_dir, "final_report.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(final_markdown)
        
    print(f"Final Report saved to {report_path}")
    
    # State update is not strictly necessary as this is the end of the line, 
    # but we can pass the path back.
    return state
