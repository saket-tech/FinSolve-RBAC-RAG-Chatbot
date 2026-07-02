# Azure Deployment Guide — FinSolve RBAC Chatbot

Deploy the FastAPI backend and Streamlit UI to **Azure Container Apps** using Docker images from **Azure Container Registry (ACR)**.

## Architecture on Azure

```
Internet
   │
   ├── Streamlit Container App (port 8501) ──► API Container App (port 8000)
   │                                              │
   │                                              └── Chroma index (built on startup)
   └── Azure Container Registry (stores Docker images)
```

## Prerequisites

- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) installed and logged in
- [Docker](https://www.docker.com/) installed locally (for building images)
- Groq API key

## Step 1 — Set variables

```bash
# Customize these
RESOURCE_GROUP=finsolve-rg
LOCATION=centralindia
ACR_NAME=finsolveacr$RANDOM
ENV_NAME=finsolve-env
API_APP=finsolve-api
UI_APP=finsolve-ui
```

## Step 2 — Create Azure resources

```bash
az login
az group create --name $RESOURCE_GROUP --location $LOCATION

az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

az containerapp env create \
  --name $ENV_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

## Step 3 — Build and push Docker images

```bash
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer -o tsv)
az acr login --name $ACR_NAME

docker build -f Dockerfile.api -t $ACR_LOGIN_SERVER/finsolve-api:latest .
docker build -f Dockerfile.streamlit -t $ACR_LOGIN_SERVER/finsolve-ui:latest .

docker push $ACR_LOGIN_SERVER/finsolve-api:latest
docker push $ACR_LOGIN_SERVER/finsolve-ui:latest
```

## Step 4 — Deploy API Container App

```bash
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

az containerapp create \
  --name $API_APP \
  --resource-group $RESOURCE_GROUP \
  --environment $ENV_NAME \
  --image $ACR_LOGIN_SERVER/finsolve-api:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_NAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8000 \
  --ingress external \
  --cpu 1.0 --memory 2.0Gi \
  --min-replicas 1 --max-replicas 2 \
  --env-vars \
    GROQ_API_KEY=your_groq_api_key \
    JWT_SECRET=your-strong-jwt-secret \
    GROQ_MODEL=llama-3.3-70b-versatile
```

Get the API URL:

```bash
API_URL=$(az containerapp show --name $API_APP --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)
echo "https://$API_URL"
```

## Step 5 — Deploy Streamlit Container App

```bash
az containerapp create \
  --name $UI_APP \
  --resource-group $RESOURCE_GROUP \
  --environment $ENV_NAME \
  --image $ACR_LOGIN_SERVER/finsolve-ui:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_NAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8501 \
  --ingress external \
  --cpu 0.5 --memory 1.0Gi \
  --min-replicas 1 --max-replicas 2 \
  --env-vars API_URL=https://$API_URL
```

Get the UI URL:

```bash
UI_URL=$(az containerapp show --name $UI_APP --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)
echo "Open: https://$UI_URL"
```

## Step 6 — Verify deployment

```bash
curl https://$API_URL/health
```

Log in to the Streamlit UI with `finance_user` / `finsolve123` and ask a finance question.

## GitHub Actions CI/CD

The workflow at `.github/workflows/azure-deploy.yml` automates build and deploy on push to `main`.

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `AZURE_CREDENTIALS` | Service principal JSON from `az ad sp create-for-rbac` |
| `ACR_NAME` | Azure Container Registry name |
| `AZURE_RESOURCE_GROUP` | Resource group name |
| `CONTAINERAPPS_ENV` | Container Apps environment name |
| `GROQ_API_KEY` | Groq API key |
| `JWT_SECRET` | Strong JWT signing secret |

Create service principal:

```bash
az ad sp create-for-rbac \
  --name "finsolve-github-actions" \
  --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/$RESOURCE_GROUP \
  --sdk-auth
```

Copy the JSON output into GitHub secret `AZURE_CREDENTIALS`.

## Notes

- **Chroma persistence:** The vector index is rebuilt on API startup if empty. For production, mount Azure Files to `/app/chroma_db` or run `build_index` in a CI step and bake into the image.
- **Cold start:** First request may be slow while embeddings model loads (~30s).
- **Costs:** Container Apps Basic ACR + 2 apps ≈ low cost for demo; scale down when not in use.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| UI cannot reach API | Ensure `API_URL` on Streamlit app uses `https://` and the correct API FQDN |
| 401 on chat | Token expired — log in again |
| Empty answers | Check `GROQ_API_KEY` on API container app |
| Index empty | Check API logs; ensure `DS-RPC-01/data` is in the Docker image |
