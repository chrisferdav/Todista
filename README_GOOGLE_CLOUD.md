# 🤖 Bot de Telegram - Despliegue en Google Cloud

Este bot convierte notas de voz en tareas estructuradas usando IA. Está optimizado para desplegarse en Google Cloud Run.

## 🚀 Despliegue Rápido

### Opción 1: Despliegue Manual (Recomendado para principiantes)

1. **Instalar Google Cloud CLI**
   ```bash
   # Windows (PowerShell)
   winget install Google.CloudSDK
   
   # O descargar desde: https://cloud.google.com/sdk/docs/install
   ```

2. **Crear proyecto en Google Cloud**
   ```bash
   gcloud projects create todista-bot-[TU_ID_UNICO]
   gcloud config set project todista-bot-[TU_ID_UNICO]
   ```

3. **Configurar secretos**
   ```bash
   # En PowerShell, ejecutar:
   ./setup-secrets.sh todista-bot-[TU_ID_UNICO]
   ```

4. **Desplegar**
   ```bash
   ./deploy.sh todista-bot-[TU_ID_UNICO]
   ```

### Opción 2: Despliegue Automático con GitHub Actions

1. **Configurar secretos en GitHub:**
   - Ve a tu repositorio → Settings → Secrets and variables → Actions
   - Agrega estos secretos:
     - `GCP_PROJECT_ID`: tu-project-id
     - `GCP_SA_KEY`: clave de cuenta de servicio (JSON)
     - `TELEGRAM_TOKEN`: tu-token-de-telegram
     - `OPENAI_API_KEY`: tu-openai-key
     - `GEMINI_API_KEY`: tu-gemini-key
     - `TODOIST_API_TOKEN`: tu-todoist-token

2. **Hacer push al repositorio**
   ```bash
   git add .
   git commit -m "Configurar despliegue en Google Cloud"
   git push origin main
   ```

## 🔧 Configuración Detallada

### 1. Crear Cuenta de Servicio

```bash
# Crear cuenta de servicio
gcloud iam service-accounts create todista-bot-sa \
  --display-name="Todista Bot Service Account"

# Dar permisos necesarios
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

### 2. Habilitar APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 3. Configurar Variables de Entorno

```bash
# Usando Secret Manager (recomendado)
gcloud run services update todista-bot \
  --set-env-vars="TELEGRAM_TOKEN=projects/[PROJECT_ID]/secrets/telegram-token/versions/latest" \
  --set-env-vars="OPENAI_API_KEY=projects/[PROJECT_ID]/secrets/openai-api-key/versions/latest" \
  --set-env-vars="GEMINI_API_KEY=projects/[PROJECT_ID]/secrets/gemini-api-key/versions/latest" \
  --set-env-vars="TODOIST_API_TOKEN=projects/[PROJECT_ID]/secrets/todoist-api-token/versions/latest"

# O usando variables directas (menos seguro)
gcloud run services update todista-bot \
  --set-env-vars="TELEGRAM_TOKEN=tu_token,OPENAI_API_KEY=tu_key,GEMINI_API_KEY=tu_key,TODOIST_API_TOKEN=tu_token"
```

## 📊 Monitoreo

### Ver Logs
```bash
# Logs en tiempo real
gcloud logs tail --service todista-bot

# Logs específicos
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=todista-bot"
```

### Métricas en Consola
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Navega a Cloud Run
3. Selecciona tu servicio `todista-bot`
4. Ve a la pestaña "Métricas"

## 🛠️ Troubleshooting

### Problemas Comunes

**Error: "Permission denied"**
```bash
gcloud auth login
gcloud config set project [TU_PROJECT_ID]
```

**Error: "Service not found"**
```bash
# Verificar que el servicio existe
gcloud run services list --region=us-central1

# Si no existe, desplegar de nuevo
./deploy.sh [TU_PROJECT_ID]
```

**Error: "Variables de entorno no configuradas"**
```bash
# Configurar variables
gcloud run services update todista-bot --set-env-vars="VARIABLE=valor"

# O usar Secret Manager
./setup-secrets.sh [TU_PROJECT_ID]
```

**Error: "Memory limit exceeded"**
```bash
# Aumentar memoria
gcloud run services update todista-bot --memory 1Gi
```

### Reiniciar Servicio
```bash
# Reiniciar completamente
gcloud run services update todista-bot --no-traffic
gcloud run services update todista-bot --to-latest
```

## 💰 Costos

**Capa Gratuita de Google Cloud Run:**
- 2 millones de requests gratuitos por mes
- 360,000 vCPU-seconds gratuitos por mes
- 180,000 GiB-seconds de memoria gratuitos por mes

**Para un bot típico:**
- ~$0-5 USD por mes (dentro de la capa gratuita)
- Solo pagas si excedes los límites

## 🔐 Seguridad

### Mejores Prácticas

1. **Usar Secret Manager** en lugar de variables de entorno directas
2. **Configurar IAM apropiadamente** con permisos mínimos
3. **Habilitar auditoría** para monitorear accesos
4. **Rotar claves** regularmente

### Configurar Auditoría
```bash
# Habilitar auditoría
gcloud services enable cloudaudit.googleapis.com

# Ver logs de auditoría
gcloud logging read "protoPayload.serviceName=run.googleapis.com"
```

## 📞 Soporte

### Comandos Útiles

```bash
# Ver estado del servicio
gcloud run services describe todista-bot --region=us-central1

# Ver revisiones
gcloud run revisions list --service todista-bot --region=us-central1

# Ver logs de errores
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR"

# Actualizar imagen
gcloud builds submit --tag gcr.io/[PROJECT_ID]/todista-bot
gcloud run services update todista-bot --image gcr.io/[PROJECT_ID]/todista-bot
```

### Recursos Adicionales

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Secret Manager Guide](https://cloud.google.com/secret-manager/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)

## 🎉 ¡Listo!

Tu bot estará disponible 24/7 con:
- ✅ Escalado automático
- ✅ Alta disponibilidad
- ✅ Monitoreo integrado
- ✅ Costos mínimos
- ✅ Seguridad robusta 