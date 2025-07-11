#!/bin/bash

# Script de despliegue para Google Cloud Run
# Uso: ./deploy.sh [PROJECT_ID]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si se proporcionó PROJECT_ID
if [ $# -eq 0 ]; then
    print_error "Debes proporcionar el PROJECT_ID como argumento"
    echo "Uso: ./deploy.sh [PROJECT_ID]"
    echo "Ejemplo: ./deploy.sh todista-bot-123456"
    exit 1
fi

PROJECT_ID=$1
SERVICE_NAME="todista-bot"
REGION="us-central1"

print_status "🚀 Iniciando despliegue en Google Cloud Run..."
print_status "Proyecto: $PROJECT_ID"
print_status "Servicio: $SERVICE_NAME"
print_status "Región: $REGION"

# Verificar que gcloud esté instalado
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud CLI no está instalado"
    echo "Instala desde: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar autenticación
print_status "Verificando autenticación..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    print_warning "No hay sesión activa. Iniciando login..."
    gcloud auth login
fi

# Configurar proyecto
print_status "Configurando proyecto..."
gcloud config set project $PROJECT_ID

# Verificar que el proyecto existe
if ! gcloud projects describe $PROJECT_ID &> /dev/null; then
    print_error "El proyecto $PROJECT_ID no existe"
    echo "Crea el proyecto primero con: gcloud projects create $PROJECT_ID"
    exit 1
fi

# Habilitar APIs necesarias
print_status "Habilitando APIs necesarias..."
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet

# Verificar variables de entorno
print_status "Verificando variables de entorno..."
if [ -z "$TELEGRAM_TOKEN" ] || [ -z "$OPENAI_API_KEY" ] || [ -z "$GEMINI_API_KEY" ]; then
    print_warning "Variables de entorno no configuradas"
    echo "Configura las siguientes variables:"
    echo "export TELEGRAM_TOKEN='tu_token_aqui'"
    echo "export OPENAI_API_KEY='tu_openai_key_aqui'"
    echo "export GEMINI_API_KEY='tu_gemini_key_aqui'"
    echo "export TODOIST_API_TOKEN='tu_todoist_token_aqui'"
    echo ""
    read -p "¿Continuar sin configurar variables de entorno? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build y push de la imagen
print_status "Construyendo imagen Docker..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME --quiet

# Desplegar en Cloud Run
print_status "Desplegando en Cloud Run..."

# Comando base
DEPLOY_CMD="gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 1 \
  --timeout 300 \
  --quiet"

# Agregar variables de entorno si están configuradas
if [ ! -z "$TELEGRAM_TOKEN" ] && [ ! -z "$OPENAI_API_KEY" ] && [ ! -z "$GEMINI_API_KEY" ]; then
    ENV_VARS="TELEGRAM_TOKEN=$TELEGRAM_TOKEN,OPENAI_API_KEY=$OPENAI_API_KEY,GEMINI_API_KEY=$GEMINI_API_KEY"
    if [ ! -z "$TODOIST_API_TOKEN" ]; then
        ENV_VARS="$ENV_VARS,TODOIST_API_TOKEN=$TODOIST_API_TOKEN"
    fi
    DEPLOY_CMD="$DEPLOY_CMD --set-env-vars=\"$ENV_VARS\""
fi

# Ejecutar despliegue
eval $DEPLOY_CMD

# Obtener URL del servicio
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

print_status "✅ Despliegue completado exitosamente!"
print_status "URL del servicio: $SERVICE_URL"

# Mostrar información adicional
print_status "📊 Información del servicio:"
gcloud run services describe $SERVICE_NAME --region=$REGION --format="table(metadata.name,status.url,spec.template.spec.containers[0].resources.limits.memory,spec.template.spec.containers[0].resources.limits.cpu)"

print_status "📝 Comandos útiles:"
echo "  Ver logs: gcloud logs tail --service $SERVICE_NAME"
echo "  Ver estado: gcloud run services describe $SERVICE_NAME --region=$REGION"
echo "  Actualizar variables: gcloud run services update $SERVICE_NAME --set-env-vars=\"VARIABLE=valor\""
echo "  Reiniciar: gcloud run services update $SERVICE_NAME --to-latest"

print_status "🎉 ¡Tu bot está listo para usar!" 