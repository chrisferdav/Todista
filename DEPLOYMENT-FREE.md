# 🆓 Guía de Deployment GRATUITO - Bot de Telegram

## 🎯 **RECOMENDADO: Render.com**

### **✅ Ventajas:**
- **100% GRATIS**: 750 horas/mes (suficiente para 24/7)
- **Sin tarjeta de crédito**
- **Muy fácil de usar**
- **Deployment automático**
- **Logs en tiempo real**

---

## 🚀 **Paso a Paso: Render.com**

### **Paso 1: Preparar repositorio GitHub**

1. **Crear repositorio en GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Bot de Telegram"
   ```

2. **Subir a GitHub:**
   ```bash
   git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
   git branch -M main
   git push -u origin main
   ```

### **Paso 2: Crear cuenta en Render**

1. **Ir a [render.com](https://render.com)**
2. **Registrarse** con GitHub
3. **No requiere tarjeta de crédito**

### **Paso 3: Crear servicio**

1. **Click "New +"**
2. **Seleccionar "Web Service"**
3. **Conectar repositorio de GitHub**
4. **Seleccionar tu repositorio**

### **Paso 4: Configurar servicio**

```
Name: telegram-bot
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: python main.py
```

### **Paso 5: Variables de entorno**

En **Environment Variables** agregar:

```
TELEGRAM_TOKEN=TU_TELEGRAM_TOKEN_AQUI
OPENAI_API_KEY=TU_OPENAI_API_KEY_AQUI
GEMINI_API_KEY=TU_GEMINI_API_KEY_AQUI
TODOIST_API_TOKEN=TU_TODOIST_API_TOKEN_AQUI
```

### **Paso 6: Deploy**

1. **Click "Create Web Service"**
2. **Render construirá automáticamente**
3. **El bot estará online en 2-3 minutos**

---

## 🔄 **Actualizaciones**

Para actualizar el bot:

```bash
git add .
git commit -m "Update bot"
git push origin main
```

Render detectará automáticamente los cambios y redeployará.

---

## 🆘 **Solución de Problemas**

### **Bot no responde:**
1. Ir a **Logs** en Render
2. Verificar variables de entorno
3. Comprobar que el bot inició correctamente

### **Error de build:**
1. Verificar `requirements.txt`
2. Revisar logs de build
3. Comprobar sintaxis de Python

### **Error de memoria:**
1. Render asigna 512MB por defecto
2. Suficiente para el bot

---

## 💰 **Costos**

- **Render**: **GRATIS** (750 horas/mes)
- **OpenAI**: ~$0.006/minuto de audio
- **Google Gemini**: Gratis (con límites)
- **Total**: **$0-5/mes** (solo OpenAI)

---

## 🆓 **Alternativas Gratuitas**

### **2. Railway.com**
- **Gratis**: $5 crédito/mes
- **Requiere tarjeta de crédito**
- **Muy fácil**

### **3. Google Cloud Run**
- **Gratis**: 2M requests/mes
- **Sin tarjeta de crédito**
- **Más complejo**

### **4. Heroku**
- **Gratis**: 550-1000 horas/mes
- **Requiere tarjeta de crédito**
- **Fácil**

---

## 📱 **Resultado Final**

Una vez desplegado:
- ✅ **Funciona 24/7**
- ✅ **Accesible desde celular**
- ✅ **No necesitas terminal**
- ✅ **Completamente GRATIS**
- ✅ **Actualizaciones automáticas** 