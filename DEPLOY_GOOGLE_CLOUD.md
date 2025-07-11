# 🚀 Despliegue en Google Cloud Run

Esta guía te ayudará a desplegar tu bot de Telegram en Google Cloud Run de forma gratuita y confiable.

## 📋 Prerrequisitos

1. **Cuenta de Google Cloud**
   - Ve a [Google Cloud Console](https://console.cloud.google.com/)
   - Crea una cuenta gratuita (incluye $300 de créditos)

2. **Google Cloud CLI**
   - Descarga e instala [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
   - Ejecuta `gcloud init` para configurar tu proyecto

3. **Docker** (opcional, para testing local)
   - Instala [Docker Desktop](https://www.docker.com/products/docker-desktop/)

## 🔧 Configuración Inicial

### 1. Crear Proyecto en Google Cloud

```bash
# Crear nuevo proyecto
gcloud projects create todista-bot-[TU_ID_UNICO]

# Configurar el proyecto
gcloud config set project todista-bot-[TU_ID_UNICO]

# Habilitar APIs necesarias
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 2. Configurar Variables de Entorno

```bash
# Configurar variables de entorno (reemplaza con tus valores reales)
gcloud run services update todista-bot \
  --set-env-vars="TELEGRAM_TOKEN=tu_token_aqui" \
  --set-env-vars="OPENAI_API_KEY=tu_openai_key_aqui" \
  --set-env-vars="GEMINI_API_KEY=tu_gemini_key_aqui" \
  --set-env-vars="TODOIST_API_TOKEN=tu_todoist_token_aqui"
```

## 🚀 Despliegue Automático

### Opción 1: Despliegue Manual

```bash
# Build y push de la imagen
gcloud builds submit --tag gcr.io/[PROJECT_ID]/todista-bot

# Desplegar en Cloud Run
gcloud run deploy todista-bot \
  --image gcr.io/[PROJECT_ID]/todista-bot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 1 \
  --timeout 300
```

### Opción 2: Despliegue Automático con Cloud Build

```bash
# Configurar variables de sustitución
gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_TELEGRAM_TOKEN="tu_token",_OPENAI_API_KEY="tu_key",_GEMINI_API_KEY="tu_key",_TODOIST_API_TOKEN="tu_token"
```

## 🔄 Despliegue Continuo

### Configurar GitHub Actions (Recomendado)

1. **Crear Secretos en GitHub:**
   - Ve a tu repositorio → Settings → Secrets and variables → Actions
   - Agrega los siguientes secretos:
     - `GCP_PROJECT_ID`
     - `GCP_SA_KEY` (clave de cuenta de servicio)

2. **Crear archivo `.github/workflows/deploy.yml`:**

```yaml
name: Deploy to Google Cloud Run

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Google Cloud CLI
      uses: google-github-actions/setup-gcloud@v0
      with:
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        project_id: ${{ secrets.GCP_PROJECT_ID }}
    
    - name: Build and Deploy
      run: |
        gcloud builds submit --tag gcr.io/${{ secrets.GCP_PROJECT_ID }}/todista-bot
        gcloud run deploy todista-bot \
          --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/todista-bot \
          --platform managed \
          --region us-central1 \
          --allow-unauthenticated \
          --memory 512Mi \
          --cpu 1 \
          --max-instances 1 \
          --timeout 300
```

## 💰 Costos

**Google Cloud Run tiene una capa gratuita generosa:**
- 2 millones de requests gratuitos por mes
- 360,000 vCPU-seconds gratuitos por mes
- 180,000 GiB-seconds de memoria gratuitos por mes

**Para un bot de Telegram típico:**
- ~$0-5 USD por mes (dentro de la capa gratuita)
- Solo pagas si excedes los límites gratuitos

## 🔍 Monitoreo

### Ver Logs

```bash
# Ver logs en tiempo real
gcloud logs tail --service todista-bot

# Ver logs específicos
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=todista-bot"
```

### Métricas en Google Cloud Console

1. Ve a Cloud Run en la consola
2. Selecciona tu servicio `todista-bot`
3. Ve a la pestaña "Métricas" para ver:
   - Requests por segundo
   - Latencia
   - Uso de CPU y memoria
   - Errores

## 🛠️ Troubleshooting

### Problemas Comunes

1. **Error de permisos:**
   ```bash
   gcloud auth login
   gcloud config set project [TU_PROJECT_ID]
   ```

2. **Error de variables de entorno:**
   ```bash
   gcloud run services update todista-bot --set-env-vars="VARIABLE=valor"
   ```

3. **Error de memoria:**
   ```bash
   gcloud run services update todista-bot --memory 1Gi
   ```

4. **Reiniciar servicio:**
   ```bash
   gcloud run services update todista-bot --no-traffic
   gcloud run services update todista-bot --to-latest
   ```

### Verificar Estado

```bash
# Ver estado del servicio
gcloud run services describe todista-bot --region us-central1

# Ver revisiones
gcloud run revisions list --service todista-bot --region us-central1
```

## 🔐 Seguridad

### Mejores Prácticas

1. **Usar Secret Manager para variables sensibles:**
   ```bash
   # Crear secretos
   echo -n "tu_token" | gcloud secrets create telegram-token --data-file=-
   
   # Usar en Cloud Run
   gcloud run services update todista-bot \
     --set-env-vars="TELEGRAM_TOKEN=projects/[PROJECT_ID]/secrets/telegram-token/versions/latest"
   ```

2. **Configurar IAM apropiadamente:**
   ```bash
   # Dar permisos mínimos necesarios
   gcloud projects add-iam-policy-binding [PROJECT_ID] \
     --member="serviceAccount:[SERVICE_ACCOUNT]" \
     --role="roles/run.invoker"
   ```

## 📞 Soporte

Si tienes problemas:

1. **Revisar logs:** `gcloud logs tail --service todista-bot`
2. **Verificar configuración:** `gcloud run services describe todista-bot`
3. **Reiniciar servicio:** `gcloud run services update todista-bot --to-latest`

## 🎉 ¡Listo!

Tu bot estará disponible 24/7 en Google Cloud Run con:
- ✅ Escalado automático
- ✅ Alta disponibilidad
- ✅ Monitoreo integrado
- ✅ Costos mínimos
- ✅ Despliegue continuo (con GitHub Actions) 