# Azure Resources Verification Script
# Run this to check what resources you've created

Write-Host "🔍 Checking Azure Resources..." -ForegroundColor Cyan
Write-Host ""

# Variables
$RESOURCE_GROUP = "finsolve-rg"

# Check if logged in
Write-Host "1️⃣ Checking Azure login..." -ForegroundColor Yellow
$account = az account show 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Not logged in to Azure. Run: az login" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Logged in to Azure" -ForegroundColor Green
$accountInfo = $account | ConvertFrom-Json
Write-Host "   Subscription: $($accountInfo.name)" -ForegroundColor Gray
Write-Host ""

# Check Resource Group
Write-Host "2️⃣ Checking Resource Group..." -ForegroundColor Yellow
$rg = az group show --name $RESOURCE_GROUP 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Resource Group exists: $RESOURCE_GROUP" -ForegroundColor Green
    $rgInfo = $rg | ConvertFrom-Json
    Write-Host "   Location: $($rgInfo.location)" -ForegroundColor Gray
} else {
    Write-Host "❌ Resource Group NOT found: $RESOURCE_GROUP" -ForegroundColor Red
    Write-Host "   Create it with: az group create --name $RESOURCE_GROUP --location centralindia" -ForegroundColor Yellow
}
Write-Host ""

# Check Container Registry
Write-Host "3️⃣ Checking Container Registry..." -ForegroundColor Yellow
$acrList = az acr list --resource-group $RESOURCE_GROUP 2>$null | ConvertFrom-Json
if ($acrList.Count -gt 0) {
    foreach ($acr in $acrList) {
        Write-Host "✅ Container Registry exists: $($acr.name)" -ForegroundColor Green
        Write-Host "   Login Server: $($acr.loginServer)" -ForegroundColor Gray
        Write-Host "   SKU: $($acr.sku.name)" -ForegroundColor Gray
    }
} else {
    Write-Host "❌ No Container Registry found" -ForegroundColor Red
    Write-Host "   Create it with: az acr create --resource-group $RESOURCE_GROUP --name finsolveacrXXXX --sku Basic --admin-enabled true" -ForegroundColor Yellow
}
Write-Host ""

# Check Container Apps Environment
Write-Host "4️⃣ Checking Container Apps Environment..." -ForegroundColor Yellow
$envList = az containerapp env list --resource-group $RESOURCE_GROUP 2>$null | ConvertFrom-Json
if ($envList.Count -gt 0) {
    foreach ($env in $envList) {
        Write-Host "✅ Container Apps Environment exists: $($env.name)" -ForegroundColor Green
        Write-Host "   Location: $($env.location)" -ForegroundColor Gray
    }
} else {
    Write-Host "❌ No Container Apps Environment found" -ForegroundColor Red
    Write-Host "   Create it with: az containerapp env create --name finsolve-env --resource-group $RESOURCE_GROUP --location centralindia" -ForegroundColor Yellow
}
Write-Host ""

# Check Container Apps
Write-Host "5️⃣ Checking Container Apps..." -ForegroundColor Yellow
$appList = az containerapp list --resource-group $RESOURCE_GROUP 2>$null | ConvertFrom-Json
if ($appList.Count -gt 0) {
    foreach ($app in $appList) {
        Write-Host "✅ Container App exists: $($app.name)" -ForegroundColor Green
        Write-Host "   URL: https://$($app.properties.configuration.ingress.fqdn)" -ForegroundColor Cyan
        Write-Host "   Status: $($app.properties.provisioningState)" -ForegroundColor Gray
    }
} else {
    Write-Host "⚠️  No Container Apps deployed yet" -ForegroundColor Yellow
    Write-Host "   These will be created by GitHub Actions deployment" -ForegroundColor Gray
}
Write-Host ""

# Summary
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📊 SUMMARY" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# List all resources in the resource group
Write-Host "All resources in ${RESOURCE_GROUP}:" -ForegroundColor Yellow
az resource list --resource-group $RESOURCE_GROUP --output table 2>$null
Write-Host ""

Write-Host "✅ Verification complete!" -ForegroundColor Green
