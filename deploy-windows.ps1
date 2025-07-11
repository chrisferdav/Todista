# Script de despliegue para Google Cloud Run en Windows PowerShell
# Uso: .\deploy-windows.ps1 [PROJECT_ID]

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId
)

# Configurar colores para output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"

# Función para imprimir mensajes
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

Write-Status "🚀 Iniciando despliegue en Google Cloud Run..."
Write-Status "Proyecto: $ProjectId"
Write-Status "Servicio: todista-bot"
Write-Status "Región: us-central1"

# Verificar que gcloud esté instalado
try {
    $null = gcloud --version
} catch {
    Write-Error "Google Cloud CLI no está instalado"
    Write-Host "Instala desde: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Verificar autenticación
Write-Status "Verificando autenticación..."
$authStatus = gcloud auth list --filter=status:ACTIVE --format="value(account)"
if (-not $authStatus) {
    Write-Warning "No hay sesión activa. Iniciando login..."
    gcloud auth login
}

# Configurar proyecto
Write-Status "Configurando proyecto..."
gcloud config set project $ProjectId

# Verificar que el proyecto existe
try {
    $null = gcloud projects describe $ProjectId
} catch {
    Write-Error "El proyecto $ProjectId no existe"
    Write-Host "Crea el proyecto primero con: gcloud projects create $ProjectId"
    exit 1
}

# Habilitar APIs necesarias
Write-Status "Habilitando APIs necesarias..."
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet

# Verificar variables de entorno
Write-Status "Verificando variables de entorno..."
$envVars = @{
    "TELEGRAM_TOKEN" = $env:TELEGRAM_TOKEN
    "OPENAI_API_KEY" = $env:OPENAI_API_KEY
    "GEMINI_API_KEY" = $env:GEMINI_API_KEY
    "TODOIST_API_TOKEN" = $env:TODOIST_API_TOKEN
}

$missingVars = @()
foreach ($var in $envVars.Keys) {
    if (-not $envVars[$var]) {
        $missingVars += $var
    }
}

if ($missingVars.Count -gt 0) {
    Write-Warning "Variables de entorno no configuradas: $($missingVars -join ', ')"
    Write-Host "Configura las siguientes variables:"
    Write-Host "`$env:TELEGRAM_TOKEN = 'tu_token_aqui'"
    Write-Host "`$env:OPENAI_API_KEY = 'tu_openai_key_aqui'"
    Write-Host "`$env:GEMINI_API_KEY = 'tu_gemini_key_aqui'"
    Write-Host "`$env:TODOIST_API_TOKEN = 'tu_todoist_token_aqui'"
    Write-Host ""
    $continue = Read-Host "¿Continuar sin configurar variables de entorno? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}

# Build y push de la imagen
Write-Status "Construyendo imagen Docker..."
gcloud builds submit --tag "gcr.io/$ProjectId/todista-bot" --quiet

# Desplegar en Cloud Run
Write-Status "Desplegando en Cloud Run..."

# Comando base
$deployCmd = @(
    "gcloud", "run", "deploy", "todista-bot",
    "--image", "gcr.io/$ProjectId/todista-bot",
    "--platform", "managed",
    "--region", "us-central1",
    "--allow-unauthenticated",
    "--memory", "512Mi",
    "--cpu", "1",
    "--max-instances", "1",
    "--timeout", "300",
    "--quiet"
)

# Agregar variables de entorno si están configuradas
$envVarsString = @()
if ($env:TELEGRAM_TOKEN -and $env:OPENAI_API_KEY -and $env:GEMINI_API_KEY) {
    $envVarsString += "TELEGRAM_TOKEN=$($env:TELEGRAM_TOKEN)"
    $envVarsString += "OPENAI_API_KEY=$($env:OPENAI_API_KEY)"
    $envVarsString += "GEMINI_API_KEY=$($env:GEMINI_API_KEY)"
    
    if ($env:TODOIST_API_TOKEN) {
        $envVarsString += "TODOIST_API_TOKEN=$($env:TODOIST_API_TOKEN)"
    }
    
    $deployCmd += "--set-env-vars"
    $deployCmd += ($envVarsString -join ",")
}

# Ejecutar despliegue
& $deployCmd[0] $deployCmd[1..($deployCmd.Length-1)]

# Obtener URL del servicio
$serviceUrl = gcloud run services describe todista-bot --region=us-central1 --format="value(status.url)"

Write-Status "✅ Despliegue completado exitosamente!"
Write-Status "URL del servicio: $serviceUrl"

# Mostrar información adicional
Write-Status "📊 Información del servicio:"
gcloud run services describe todista-bot --region=us-central1 --format="table(metadata.name,status.url,spec.template.spec.containers[0].resources.limits.memory,spec.template.spec.containers[0].resources.limits.cpu)"

Write-Status "📝 Comandos útiles:"
Write-Host "  Ver logs: gcloud logs tail --service todista-bot"
Write-Host "  Ver estado: gcloud run services describe todista-bot --region=us-central1"
Write-Host "  Actualizar variables: gcloud run services update todista-bot --set-env-vars=`"VARIABLE=valor`""
Write-Host "  Reiniciar: gcloud run services update todista-bot --to-latest"

Write-Status "🎉 ¡Tu bot está listo para usar!" 