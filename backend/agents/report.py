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
        ("system", """You are a Senior Data Science Consultant writing a high-quality, professional Final Report for a client.

The report MUST follow this exact Markdown structure with ALL sections filled in properly:

---

# 📊 Final Data Science Report
## {project_name}

---

## 📋 Executive Summary
> A 2-3 sentence high-level business summary of what was done, what was found, and what is recommended.

---

## 1. 🔍 Data Quality & Exploratory Analysis

### Data Quality Score: X/100

Brief paragraph from analyst notes.

### Key Observations
- bullet points of important findings

---

## 2. ⚙️ Feature Engineering

### Transformations Applied
| Column | Action |
|--------|--------|
| col    | action |

---

## 3. 🤖 Model Training & Leaderboard

### Task Type: {task_type}
### Target Column: {target}

| Rank | Model | Score | Notes |
|------|-------|-------|-------|
| 1    | ...   | ...   | Best  |

### 🏆 Best Model: {best_model}

---

## 4. 🧠 Model Explainability (SHAP)

### Top Predictive Features
| Feature | Importance |
|---------|------------|
| ...     | ...        |

Brief explanation of what drives the predictions.

---

## 5. ✅ Conclusion & Recommendations

- **Recommendation 1**: ...
- **Recommendation 2**: ...
- **Next Steps**: ...

---

*Report generated autonomously by the Autonomous Data Science Platform.*

---

USE THIS STRUCTURE EXACTLY. Fill in all placeholders with real data. Use proper markdown tables for the leaderboard and features. Do NOT use LaTeX or raw code blocks."""),
        ("human", "Task: {task}\nTarget: {target}\nData Quality Score: {score}\nAnalyst Notes: {analyst_summary}\nFeatures Engineered: {features}\nLeaderboard: {leaderboard}\nBest Model: {best_model}\nTop Feature Drivers: {top_features}\nExplainability Notes: {shap_summary}\n\nWrite the full structured Markdown report now.")
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
    
    reports_dir = "reports" if not base_path.startswith("test_") else "."
    os.makedirs(reports_dir, exist_ok=True)
    
    file_prefix = os.path.splitext(os.path.basename(base_path))[0]
    report_path = os.path.join(reports_dir, f"{file_prefix}_final_report.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(final_markdown)
        
    print(f"Final Report saved to {report_path}")
    
    # State update is not strictly necessary as this is the end of the line, 
    # but we can pass the path back.
    return state
