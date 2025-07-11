# 🚀 Inicio Rápido - Google Cloud Run

## ⚡ Despliegue en 5 Minutos

### 1. Instalar Google Cloud CLI
```powershell
# En PowerShell (Windows)
winget install Google.CloudSDK

# O descargar desde: https://cloud.google.com/sdk/docs/install
```

### 2. Crear Proyecto
```bash
# Crear proyecto (reemplaza [TU_ID] con algo único)
gcloud projects create todista-bot-[TU_ID]
gcloud config set project todista-bot-[TU_ID]
```

### 3. Configurar Variables de Entorno
```powershell
# En PowerShell, configurar variables:
$env:TELEGRAM_TOKEN = "tu_token_aqui"
$env:OPENAI_API_KEY = "tu_openai_key_aqui"
$env:GEMINI_API_KEY = "tu_gemini_key_aqui"
$env:TODOIST_API_TOKEN = "tu_todoist_token_aqui"
```

### 4. Desplegar
```powershell
# En PowerShell:
.\deploy-windows.ps1 todista-bot-[TU_ID]
```

## 🎉 ¡Listo!

Tu bot estará disponible en: `https://todista-bot-[TU_ID]-[hash].run.app`

## 📋 Comandos Útiles

```bash
# Ver logs
gcloud logs tail --service todista-bot

# Ver estado
gcloud run services describe todista-bot --region=us-central1

# Reiniciar
gcloud run services update todista-bot --to-latest
```

## 🔧 Configuración Avanzada

Para configuración más segura con Secret Manager, ver: `DEPLOY_GOOGLE_CLOUD.md`

Para despliegue automático con GitHub Actions, ver: `MIGRATION_SUMMARY.md` 