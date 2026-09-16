# Autonomous Data Science Platform

An end-to-end autonomous multi-agent AI pipeline that automates the entire data science lifecycle—from feature engineering and AutoML to SHAP explainability and FastAPI deployment. 

Built as an interactive portfolio project to demonstrate orchestration of Large Language Models (LLMs) via LangGraph, alongside a full-stack Next.js and FastAPI application.

## 🚀 Features

- **Multi-Agent Orchestration**: Utilizes LangGraph to coordinate specialized agents (Supervisor, Data Analyst, Data Engineer, ML Engineer, Explainability, and Deployment).
- **Automated Machine Learning (AutoML)**: Automatically cleans data, engineers features, and trains multiple algorithms (XGBoost, Random Forest, LightGBM) to find the best model.
- **Explainable AI (XAI)**: Generates SHAP plots to provide model transparency and feature importance.
- **Instant Deployment**: Packages the winning model into a fully containerized FastAPI inference server, complete with a Dockerfile, ready for production.
- **Modern Full-Stack**: Beautiful, responsive light/dark mode dashboard built with Next.js 15, Tailwind CSS, and Shadcn UI.

## 🛠 Tech Stack

- **Frontend**: Next.js (App Router), React, Tailwind CSS, Shadcn UI
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL / SQLite
- **AI & Orchestration**: LangGraph, LangChain, Groq (Qwen/Llama models)
- **Data Science**: Pandas, Scikit-Learn, XGBoost, LightGBM, SHAP, MLflow
- **DevOps**: Docker, Docker Compose, GitHub Actions

## 📂 Architecture & Planning

The `planning/` directory contains detailed architectural diagrams covering the LangGraph state management, database schema, and automated pipeline workflows.

## ⚙️ Quick Start (Local Development)

### 1. Clone the repository
```bash
git clone https://github.com/abderrahmane0402/Autonomous_Data_Science_Platform.git
cd Autonomous_Data_Science_Platform
```

### 2. Environment Variables
Create a `.env` file in the root directory based on `.env.example`:
```bash
cp .env.example .env
```
Ensure you add your `GROQ_API_KEY` for the AI agents to function.

### 3. Run with Docker Compose
To spin up the entire stack (PostgreSQL, FastAPI Backend, Next.js Frontend):
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```
The application will be available at `http://localhost:3000`.

## 🧪 CI/CD Pipeline
This project utilizes GitHub Actions for continuous integration. On every push to `main`, the pipeline automatically lints the Python backend (`ruff`), builds the Next.js frontend, and verifies the multi-stage Docker builds.
