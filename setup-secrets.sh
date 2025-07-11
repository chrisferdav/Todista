#!/bin/bash

# Script para configurar Secret Manager en Google Cloud
# Uso: ./setup-secrets.sh [PROJECT_ID]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar argumentos
if [ $# -eq 0 ]; then
    print_error "Debes proporcionar el PROJECT_ID como argumento"
    echo "Uso: ./setup-secrets.sh [PROJECT_ID]"
    echo "Ejemplo: ./setup-secrets.sh todista-bot-123456"
    exit 1
fi

PROJECT_ID=$1

print_status "🔐 Configurando Secret Manager para $PROJECT_ID..."

# Verificar que gcloud esté instalado
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud CLI no está instalado"
    echo "Instala desde: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Configurar proyecto
gcloud config set project $PROJECT_ID

# Habilitar Secret Manager API
print_status "Habilitando Secret Manager API..."
gcloud services enable secretmanager.googleapis.com --quiet

# Función para crear secreto
create_secret() {
    local secret_name=$1
    local secret_value=$2
    
    if [ -z "$secret_value" ]; then
        print_warning "Valor vacío para $secret_name, saltando..."
        return
    fi
    
    # Crear secreto si no existe
    if ! gcloud secrets describe $secret_name &> /dev/null; then
        print_status "Creando secreto: $secret_name"
        echo -n "$secret_value" | gcloud secrets create $secret_name --data-file=-
    else
        print_status "Actualizando secreto: $secret_name"
        echo -n "$secret_value" | gcloud secrets versions add $secret_name --data-file=-
    fi
}

# Solicitar valores de los secretos
print_status "Configurando secretos..."
echo ""

read -p "Ingresa tu TELEGRAM_TOKEN: " TELEGRAM_TOKEN
create_secret "telegram-token" "$TELEGRAM_TOKEN"

read -p "Ingresa tu OPENAI_API_KEY: " OPENAI_API_KEY
create_secret "openai-api-key" "$OPENAI_API_KEY"

read -p "Ingresa tu GEMINI_API_KEY: " GEMINI_API_KEY
create_secret "gemini-api-key" "$GEMINI_API_KEY"

read -p "Ingresa tu TODOIST_API_TOKEN (opcional): " TODOIST_API_TOKEN
create_secret "todoist-api-token" "$TODOIST_API_TOKEN"

print_status "✅ Secretos configurados exitosamente!"

# Mostrar comandos para usar los secretos
print_status "📝 Para usar estos secretos en Cloud Run:"
echo ""
echo "gcloud run services update todista-bot \\"
echo "  --set-env-vars=\"TELEGRAM_TOKEN=projects/$PROJECT_ID/secrets/telegram-token/versions/latest\" \\"
echo "  --set-env-vars=\"OPENAI_API_KEY=projects/$PROJECT_ID/secrets/openai-api-key/versions/latest\" \\"
echo "  --set-env-vars=\"GEMINI_API_KEY=projects/$PROJECT_ID/secrets/gemini-api-key/versions/latest\" \\"
echo "  --set-env-vars=\"TODOIST_API_TOKEN=projects/$PROJECT_ID/secrets/todoist-api-token/versions/latest\""
echo ""

print_status "🔐 Los secretos están ahora almacenados de forma segura en Secret Manager!" 