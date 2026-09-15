from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Optional, List
import os

from backend.agents.state import AgentState

# Define the expected JSON output format for the Supervisor
class SupervisorDecision(BaseModel):
    task_type: str = Field(description="The type of machine learning task: 'classification', 'regression', or 'clustering'.")
    target_column: Optional[str] = Field(description="The name of the column to predict. Leave null if it's clustering.")
    execution_plan: List[str] = Field(description="A list of 3 to 5 step-by-step instructions for the downstream agents.")
    reasoning: str = Field(description="Brief explanation of why this task type and target column were chosen.")

def supervisor_agent_node(state: AgentState) -> AgentState:
    """
    The Supervisor Agent analyzes the dataset metadata and decides the ML approach.
    """
    print("--- SUPERVISOR AGENT THINKING ---")
    
    # Initialize the Groq LLM
    llm = ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0.0
    )
    
    # Bind the LLM to strictly output our Pydantic schema
    structured_llm = llm.with_structured_output(SupervisorDecision)
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an Expert Data Science Supervisor. Your job is to analyze dataset metadata and determine the appropriate Machine Learning task (classification, regression, clustering) and identify the most likely target variable to predict."),
        ("human", "Here is the dataset metadata:\n\nColumns and Datatypes: {datatypes}\n\nBased on these columns, what is the logical ML task? What is the target column to predict? Give me a brief execution plan for the data engineer and ML engineer.")
    ])
    
    # Chain them together
    chain = prompt | structured_llm
    
    # Execute the chain using only the metadata from the state
    metadata = state.get("dataset_metadata", {})
    datatypes = metadata.get("datatypes", {})
    
    decision: SupervisorDecision = chain.invoke({"datatypes": datatypes})
    
    print(f"Decision: {decision.task_type.upper()}")
    print(f"Target: {decision.target_column}")
    print(f"Reasoning: {decision.reasoning}")
    
    # Update the LangGraph state
    return {
        "task_type": decision.task_type,
        "target_column": decision.target_column,
        "execution_plan": decision.execution_plan
    }
