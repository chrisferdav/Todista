# 🔄 Migración de Render a Google Cloud

## 📋 Resumen de Cambios

### ✅ Archivos Creados para Google Cloud
- `Dockerfile` - Configuración de contenedor optimizada
- `requirements.txt` - Dependencias de Python con versiones específicas
- `.dockerignore` - Archivos excluidos del build
- `cloudbuild.yaml` - Configuración de Cloud Build
- `deploy.sh` - Script de despliegue para Linux/Mac
- `deploy-windows.ps1` - Script de despliegue para Windows
- `setup-secrets.sh` - Configuración de Secret Manager
- `.github/workflows/deploy.yml` - GitHub Actions para CI/CD
- `DEPLOY_GOOGLE_CLOUD.md` - Guía completa de despliegue
- `README_GOOGLE_CLOUD.md` - Documentación específica

### ❌ Archivos Eliminados de Render
- `render.yaml` - Configuración específica de Render
- `runtime.txt` - Versión de Python para Render

## 🚀 Pasos para Migrar

### 1. Preparación Inicial

```bash
# Instalar Google Cloud CLI en Windows
winget install Google.CloudSDK

# O descargar desde: https://cloud.google.com/sdk/docs/install
```

### 2. Crear Proyecto en Google Cloud

```bash
# Crear proyecto (reemplaza [TU_ID] con algo único)
gcloud projects create todista-bot-[TU_ID]

# Configurar proyecto
gcloud config set project todista-bot-[TU_ID]

# Habilitar APIs necesarias
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 3. Configurar Secretos (Recomendado)

```powershell
# En PowerShell, ejecutar:
.\setup-secrets.sh todista-bot-[TU_ID]
```

### 4. Desplegar

```powershell
# En PowerShell:
.\deploy-windows.ps1 todista-bot-[TU_ID]

# O en Linux/Mac:
./deploy.sh todista-bot-[TU_ID]
```

## 🔧 Configuración de Variables de Entorno

### Opción A: Usando Secret Manager (Recomendado)

```bash
# Configurar secretos
gcloud run services update todista-bot \
  --set-env-vars="TELEGRAM_TOKEN=projects/[PROJECT_ID]/secrets/telegram-token/versions/latest" \
  --set-env-vars="OPENAI_API_KEY=projects/[PROJECT_ID]/secrets/openai-api-key/versions/latest" \
  --set-env-vars="GEMINI_API_KEY=projects/[PROJECT_ID]/secrets/gemini-api-key/versions/latest" \
  --set-env-vars="TODOIST_API_TOKEN=projects/[PROJECT_ID]/secrets/todoist-api-token/versions/latest"
```

### Opción B: Variables Directas

```bash
# Configurar variables directas
gcloud run services update todista-bot \
  --set-env-vars="TELEGRAM_TOKEN=tu_token,OPENAI_API_KEY=tu_key,GEMINI_API_KEY=tu_key,TODOIST_API_TOKEN=tu_token"
```

## 🔄 Despliegue Automático con GitHub Actions

### 1. Configurar Secretos en GitHub

Ve a tu repositorio → Settings → Secrets and variables → Actions

Agrega estos secretos:
- `GCP_PROJECT_ID`: tu-project-id
- `GCP_SA_KEY`: clave de cuenta de servicio (JSON)
- `TELEGRAM_TOKEN`: tu-token-de-telegram
- `OPENAI_API_KEY`: tu-openai-key
- `GEMINI_API_KEY`: tu-gemini-key
- `TODOIST_API_TOKEN`: tu-todoist-token

### 2. Crear Cuenta de Servicio

```bash
# Crear cuenta de servicio
gcloud iam service-accounts create todista-bot-sa \
  --display-name="Todista Bot Service Account"

# Dar permisos
gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member="serviceAccount:todista-bot-sa@[PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member="serviceAccount:todista-bot-sa@[PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Crear y descargar clave
gcloud iam service-accounts keys create key.json \
  --iam-account=todista-bot-sa@[PROJECT_ID].iam.gserviceaccount.com
```

### 3. Subir al Repositorio

```bash
git add .
git commit -m "Migrar a Google Cloud Run"
git push origin main
```

## 📊 Ventajas de Google Cloud vs Render

| Característica | Google Cloud Run | Render |
|----------------|------------------|---------|
| **Capa Gratuita** | 2M requests/mes | 750 horas/mes |
| **Escalado** | Automático | Manual |
| **Memoria** | Hasta 32GB | Hasta 3GB |
| **CPU** | Hasta 8 vCPU | Hasta 2 vCPU |
| **Timeout** | Hasta 60 min | 15 min |
| **Regiones** | 20+ regiones | 3 regiones |
| **Monitoreo** | Integrado | Básico |
| **Secretos** | Secret Manager | Variables de entorno |
| **CI/CD** | Cloud Build + GitHub Actions | GitHub Actions |

## 🛠️ Comandos Útiles

### Monitoreo
```bash
# Ver logs en tiempo real
gcloud logs tail --service todista-bot

# Ver estado del servicio
gcloud run services describe todista-bot --region=us-central1

# Ver métricas
gcloud run services describe todista-bot --region=us-central1 --format="table(metadata.name,status.url,spec.template.spec.containers[0].resources.limits.memory,spec.template.spec.containers[0].resources.limits.cpu)"
```

### Mantenimiento
```bash
# Reiniciar servicio
gcloud run services update todista-bot --to-latest

# Actualizar variables
gcloud run services update todista-bot --set-env-vars="VARIABLE=valor"

# Aumentar memoria si es necesario
gcloud run services update todista-bot --memory 1Gi
```

### Troubleshooting
```bash
# Ver logs de errores
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR"

# Ver revisiones
gcloud run revisions list --service todista-bot --region=us-central1

# Verificar configuración
gcloud run services describe todista-bot --region=us-central1 --format="yaml"
```

## 💰 Costos Estimados

**Google Cloud Run (Capa Gratuita):**
- 2 millones de requests gratuitos por mes
- 360,000 vCPU-seconds gratuitos por mes
- 180,000 GiB-seconds de memoria gratuitos por mes

**Para un bot típico:**
- ~$0-5 USD por mes (dentro de la capa gratuita)
- Solo pagas si excedes los límites

## 🎉 ¡Migración Completada!

Tu bot ahora está optimizado para Google Cloud Run con:

✅ **Mejor rendimiento** - Escalado automático y más recursos
✅ **Mayor confiabilidad** - 99.9% uptime garantizado
✅ **Mejor monitoreo** - Logs y métricas integrados
✅ **Más seguridad** - Secret Manager para variables sensibles
✅ **Menor costo** - Capa gratuita más generosa
✅ **CI/CD automático** - Despliegue con GitHub Actions

## 📞 Soporte

Si tienes problemas durante la migración:

1. **Revisar logs:** `gcloud logs tail --service todista-bot`
2. **Verificar configuración:** `gcloud run services describe todista-bot`
3. **Reiniciar servicio:** `gcloud run services update todista-bot --to-latest`
4. **Consultar documentación:** `DEPLOY_GOOGLE_CLOUD.md`

¡Tu bot estará disponible 24/7 en Google Cloud Run! 🚀 