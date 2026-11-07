# 🥋 TKD Intelligence AI — AI-Powered Taekwondo Assistant

**Your intelligent Taekwondo companion for Athletes, Coaches, and Referees.**

TKD Intelligence is a multi-agent AI application designed to make Taekwondo knowledge more accessible. It uses Generative AI, Retrieval-Augmented Generation (RAG), and specialized AI agents to provide information about World Taekwondo rules, training, fitness, and competitions.

The platform allows users to interact with an AI assistant through a simple interface and receive context-aware responses based on Taekwondo knowledge resources.

---

## 🚀 Key Features

- **Multi-Agent AI Architecture:** Uses specialized AI agents to handle different Taekwondo-related queries.
- **World Taekwondo Rules Assistant:** Answers questions about Kyorugi rules and regulations.
- **Training Assistant:** Provides training guidance, techniques, drills, and practice recommendations.
- **Fitness Assistant:** Helps with fitness, conditioning, flexibility, and physical preparation.
- **Competition Assistant:** Supports competition preparation and related Taekwondo information.
- **Retrieval-Augmented Generation (RAG):** Retrieves relevant information from Taekwondo reference documents.
- **Taekwondo Terminology:** Provides explanations of Taekwondo terminology.
- **Role-Based Workspaces:** Dedicated workspaces for Athletes, Coaches, and Referees.
- **Conversational AI:** Supports follow-up questions using session-based conversation history.
- **Free Public Access:** No subscription or payment required.

## 🤖 AI Agents

| Agent             | Responsibility                                      |
| ----------------- | --------------------------------------------------- |
| Rules Agent       | World Taekwondo rules and regulations               |
| Training Agent    | Training methods, techniques, and practice guidance |
| Fitness Agent     | Fitness, conditioning, and physical preparation     |
| Competition Agent | Competition preparation and guidance                |

A LangGraph-based supervisor analyzes incoming questions and routes them to the appropriate specialist agent.

## 🏗️ System Architecture

```text
              User
               |
               v
       Streamlit Frontend
               |
               v
          FastAPI Backend
               |
               v
       LangGraph Supervisor
               |
       Question Classification
               |
       +-------+-------+-------+
       |       |       |       |
     Rules  Training Fitness Competition
     Agent   Agent   Agent     Agent
       |       |       |       |
       +-------+-------+-------+
               |
               v
          Groq LLM
               |
               v
        RAG / Pinecone
               |
               v
        AI-Generated Answer
               |
               v
          User Interface
```

## 🛠️ Technology Stack

| Category               | Technologies               |
| ---------------------- | -------------------------- |
| Programming Language   | Python                     |
| Frontend               | Streamlit                  |
| Backend                | FastAPI                    |
| LLM                    | Groq API                   |
| AI Framework           | LangChain                  |
| Agent Orchestration    | LangGraph                  |
| Vector Database        | Pinecone                   |
| Embeddings             | Sentence Transformers      |
| Document Processing    | PyPDF                      |
| Environment Management | Python Virtual Environment |

## 📚 Knowledge Base

The application uses Taekwondo reference documents for retrieval-based responses, including:

- World Taekwondo Kyorugi Rules (January 2026).
- Kims Taekwondo Terminology Guide.
- Comprehensive Taekwondo Terminology Guide.

These documents are processed and indexed in Pinecone to support relevant information retrieval.

## 📁 Project Structure

```text
TKD-Intelligence-AI/
│
├── backend/
│   ├── agents/
│   │   ├── rules_agent.py
│   │   ├── training_agent.py
│   │   ├── fitness_agent.py
│   │   ├── competition_agent.py
│   │   └── supervisor.py
│   │
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── ingest.py
│   │   ├── ingest_terminology.py
│   │   ├── retriever.py
│   │   └── terminology_retriever.py
│   │
│   ├── workflows/
│   ├── llm.py
│   ├── main.py
│   └── requirements.txt
│
├── data/
│   ├── rules/
│   └── terminology/
│
├── frontend/
│   ├── app.py
│   └── requirements.txt
│
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/DharanidharKola/TKD-Intelligence-AI.git
```

```bash
cd TKD-Intelligence-AI
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and configure your required credentials:

```env
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

Add any additional Pinecone configuration required by your project code.

**Never upload your `.env` file or API credentials to GitHub.**

### 5. Start the FastAPI backend

From the project root:

```bash
python -m uvicorn backend.main:app --reload
```

Backend API:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Start the Streamlit frontend

Open another terminal, activate the virtual environment, and run:

```bash
python -m streamlit run frontend/app.py
```

Open the local URL displayed in the terminal, normally:

```text
http://localhost:8501
```

## 🔐 Security and Access

- Free access for users.
- No payment gateway or subscription requirement.
- API credentials must be configured through environment variables or secure hosting secrets.
- Technical errors should be logged on the server rather than exposed to users.

## 🎯 Project Objective

The goal of TKD Intelligence is to combine Artificial Intelligence and Taekwondo knowledge into a single platform that helps athletes, coaches, and referees access useful information, understand rules, improve preparation, and explore Taekwondo terminology.

## 👨‍💻 Developer

**Dharanidhar Kola**

- Email: [dharanidhar2321@gmail.com](mailto\:dharanidhar2321@gmail.com)
- LinkedIn: [https://www.linkedin.com/in/dharanidharkola/](https://www.linkedin.com/in/dharanidharkola/)

---

**TKD Intelligence — Empowering the Taekwondo community with AI.** 🥋
