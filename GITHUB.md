# GitHub Repository Setup

Follow these steps to publish the project to GitHub.

## 1. Create a new repository on GitHub

1. Go to [github.com/new](https://github.com/new)
2. Name it `ds-rpc-01` (or your preferred name)
3. Do **not** initialize with README (this project already has one)
4. Click **Create repository**

## 2. Push local code

```bash
cd D:\DS-RPC-01

git add .
git commit -m "Add FinSolve RBAC RAG chatbot with Groq, Chroma, FastAPI, Streamlit, and Azure deployment"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/ds-rpc-01.git
git push -u origin main
```

## 3. Configure GitHub Secrets for Azure CI/CD

In your GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|--------|-------|
| `AZURE_CREDENTIALS` | Service principal JSON (see azure/DEPLOY.md) |
| `ACR_NAME` | Your Azure Container Registry name |
| `ACR_PASSWORD` | ACR admin password |
| `AZURE_RESOURCE_GROUP` | e.g. `finsolve-rg` |
| `CONTAINERAPPS_ENV` | e.g. `finsolve-env` |
| `GROQ_API_KEY` | Your Groq API key |
| `JWT_SECRET` | Strong random secret |

## 4. Enable GitHub Actions

Push to `main` triggers `.github/workflows/azure-deploy.yml` after Azure resources are created (see `azure/DEPLOY.md`).
