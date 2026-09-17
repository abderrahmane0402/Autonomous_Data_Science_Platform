<div align="center">

# 🧠 Autonomous Data Science Platform

**End-to-End Multi-Agent AI Pipeline for Automated Data Science**

[![CI Pipeline](https://github.com/abderrahmane0402/Autonomous_Data_Science_Platform/actions/workflows/ci.yml/badge.svg)](https://github.com/abderrahmane0402/Autonomous_Data_Science_Platform/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=next.js&logoColor=white)](https://nextjs.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi_Agent-ff6600?logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit_Learn-1.9+-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)](https://postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Platform%20Demo-4F46E5?style=for-the-badge&logo=google-chrome&logoColor=white)](https://sabkari-dev.ddns.net/Autonomo)

Automate your entire data science lifecycle—from feature engineering and AutoML to SHAP explainability and FastAPI model deployment—using collaborating AI agents.

🌐 **Live Demo:** [https://sabkari-dev.ddns.net/Autonomo](https://sabkari-dev.ddns.net/Autonomo)
*(Note: Create an account on the live demo to begin).*

🚢 **Test Dataset:** To see the AI in action, download the classic [Titanic Dataset (CSV)](https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv). Upload it to the platform, select `Survived` as the target variable, and watch the agents build the entire pipeline!

[Features](#-key-features) • [Preview](#-preview) • [Architecture](#-architecture) • [Quickstart](#-quickstart-with-docker) • [Tech Stack](#-tech-stack) • [License](#-license)

</div>

---

## 🖼️ Preview

<div align="center">
  <img src="planning/general_workflow.png" alt="Platform Architecture Preview" width="900" style="border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);" />
  <br />
  <i>(Replace with a dashboard screenshot later)</i>
</div>

---

## ⚡ Key Features

- **🤖 Multi-Agent Orchestration**: Utilizes LangGraph to coordinate specialized agents (Supervisor, Data Analyst, Data Engineer, ML Engineer, Explainability, and Deployment).
- **📈 Automated Machine Learning (AutoML)**: Automatically cleans data, engineers features, and trains multiple algorithms (XGBoost, Random Forest, LightGBM) to find the best model.
- **🔍 Explainable AI (XAI)**: Generates detailed SHAP plots to provide model transparency, feature attribution, and global importance.
- **🚀 Instant Deployment**: Packages the winning model into a fully containerized FastAPI inference server, complete with a Dockerfile, ready for production use.
- **📱 Responsive Enterprise UI**: Clean, responsive light and dark mode dashboard built with Next.js 15, Tailwind CSS, and Shadcn UI.
- **🔒 Secure Architecture**: JWT-based authentication, stateless design with PostgreSQL, and ready for deployment on any VPS.
- **🐳 Production Ready**: Fully containerized with robust multi-stage Docker builds and automated GitHub Actions CI pipelines.

---

## 🏛️ Architecture

```mermaid
graph TD
    User([User / Browser]) -->|HTTP / HTTPS| NextJS[Next.js Frontend :3000]
    NextJS -->|REST API Proxy| FastAPI[FastAPI Backend :8000]
    
    FastAPI -->|State & Metadata| Postgres[(PostgreSQL 15)]
    FastAPI -->|Orchestration| LangGraph[LangGraph State Machine]

    LangGraph -->|Routing| Supervisor[Supervisor Agent]
    Supervisor -->|Feature Eng| DE[Data Engineer]
    Supervisor -->|Profiling| DA[Data Analyst]
    Supervisor -->|Training| MLE[ML Engineer]
    MLE -->|Experiment Tracking| MLflow[(MLflow)]
    Supervisor -->|SHAP Plots| XAI[Explainability Agent]
    Supervisor -->|FastAPI Packaging| Deploy[Deployment Agent]

    DE -.-> LLM[Groq Cloud LLM]
    DA -.-> LLM
    MLE -.-> LLM
```

*(You can find more detailed architectural diagrams in the `planning/` directory).*

---

## 🚀 Quickstart with Docker

The fastest way to spin up the Autonomous Data Science Platform locally or on a VPS is using Docker Compose:

### 1. Clone the repository
```bash
git clone https://github.com/abderrahmane0402/Autonomous_Data_Science_Platform.git
cd Autonomous_Data_Science_Platform
```

### 2. Configure environment variables
```bash
cp .env.example .env
```
Edit `.env` and provide your **Groq API Key** and JWT Secret:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
JWT_SECRET_KEY=your_super_secret_jwt_key
```

### 3. Start the entire application
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Access the application in your browser:
- **Web UI**: `http://localhost:3000` (Or your VPS public IP / Domain)
- **FastAPI Interactive Docs**: `http://localhost:8000/docs`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 15 (App Router), React, Tailwind CSS, Shadcn UI |
| **Backend API** | FastAPI, Pydantic, SQLAlchemy, Uvicorn |
| **AI Agents** | LangGraph, LangChain, Groq (Qwen/Llama) |
| **Data Science** | Pandas, Scikit-Learn, XGBoost, LightGBM, SHAP, MLflow |
| **Database** | PostgreSQL 15 (Production) / SQLite (Local) |
| **DevOps & CI** | Docker, Docker Compose, GitHub Actions |

---

## 💻 Local Development Setup

If you prefer to run the frontend and backend natively outside Docker for development:

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Ensure .env exists (create from template in root)
cp ../.env.example .env

# Start API (SQLite will be used by default)
uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
