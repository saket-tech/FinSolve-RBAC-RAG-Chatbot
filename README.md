# FinSolve RBAC RAG Chatbot

Role-based internal chatbot for **FinSolve Technologies** that authenticates users, enforces department-level access control, and answers natural language questions using **RAG** (Retrieval-Augmented Generation).

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI |
| UI | Streamlit |
| LLM | Groq (Llama 3.3 70B) |
| Vector Store | ChromaDB |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Auth | JWT + role-based access control |
| Deployment | Docker + Azure Container Apps |

## Architecture

```
User → Streamlit UI → FastAPI API → RBAC Filter → ChromaDB Retrieval → Groq LLM → Response + Sources
```

1. User logs in with username/password and receives a JWT with their role.
2. Chat queries are sent to the API with the JWT.
3. Chroma retrieves only documents from departments the role is allowed to access.
4. Groq generates an answer grounded in retrieved context with source citations.

## Role Definitions

| Role | Username | Access |
|------|----------|--------|
| Finance | `finance_user` | Financial reports, expenses, cash flow |
| Marketing | `marketing_user` | Campaign performance, ROI, customer metrics |
| HR | `hr_user` | Employee records, handbook policies |
| Engineering | `engineering_user` | Architecture, CI/CD, security docs |
| C-Level Executive | `executive_user` | **Full access** to all departments |
| Employee | `employee_user` | General policies, FAQs, handbook only |

**Demo password for all users:** `finsolve123`

## Project Structure

```
DS-RPC-01/
├── app/
│   ├── api/           # FastAPI routes and dependencies
│   ├── auth/          # Authentication, JWT, RBAC rules
│   ├── config/        # Settings from environment
│   ├── models/        # Pydantic schemas
│   └── rag/           # Embeddings, ingestion, retrieval, Groq generation
├── DS-RPC-01/data/    # Company documents by department
├── streamlit_app/     # Chat UI
├── scripts/           # Index build utility
├── azure/             # Azure deployment guide
├── chroma_db/         # Persisted vector index (generated)
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.streamlit
└── requirements.txt
```

## Local Setup

### Prerequisites

- Python 3.11+
- [Groq API key](https://console.groq.com/)

### 1. Clone and install

```bash
git clone <your-repo-url>
cd DS-RPC-01
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Build the vector index (optional — API builds on first start)

```bash
python scripts/build_index.py
```

### 4. Start the API

```bash
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Start the Streamlit UI (new terminal)

```bash
streamlit run streamlit_app/app.py
```

Open **http://localhost:8501** and log in with a demo account.

### Docker (alternative)

```bash
cp .env.example .env
# Add GROQ_API_KEY to .env
docker compose up --build
```

- API: http://localhost:8000/docs
- UI: http://localhost:8501

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/auth/login` | Authenticate and get JWT |
| POST | `/chat/query` | Ask a question (requires Bearer token) |

### Example

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"finance_user","password":"finsolve123"}'

# Chat
curl -X POST http://localhost:8000/chat/query \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"query":"What was revenue growth in 2024?"}'
```

## Usage Examples by Role

| Role | Example Query |
|------|---------------|
| Finance | "What were the main expense categories in 2024?" |
| Marketing | "How did Q2 2024 digital campaigns perform?" |
| HR | "Which employees have the highest performance ratings?" |
| Engineering | "What compliance standards does our architecture follow?" |
| Executive | "Summarize company performance across all departments" |
| Employee | "How many days of annual leave do I get?" |

## Azure Deployment

See **[azure/DEPLOY.md](azure/DEPLOY.md)** for step-by-step Azure Container Apps deployment using Azure CLI and GitHub Actions.

Quick overview:

1. Create Azure Resource Group, Container Registry, and Container Apps Environment.
2. Build and push Docker images (`Dockerfile.api`, `Dockerfile.streamlit`).
3. Deploy two Container Apps (API + Streamlit).
4. Set environment variables: `GROQ_API_KEY`, `JWT_SECRET`, `API_URL`.

## Scalability Notes

- **New roles:** Add to `app/auth/rbac.py` and create users in `app/auth/users.py`.
- **New documents:** Drop files into `DS-RPC-01/data/<department>/` and run `python scripts/build_index.py --reset`.
- **New departments:** Add a data folder and update `ROLE_DEPARTMENT_ACCESS` in `rbac.py`.

## License

Educational project for FinSolve Technologies internal chatbot challenge.
