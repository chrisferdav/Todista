# 🤖 Bot de Transcripción de Audio

Una versión simplificada del bot que se enfoca únicamente en la transcripción de notas de voz usando OpenAI Whisper.

## ✨ Características

- 🎤 **Transcripción de audio**: Convierte notas de voz en texto
- 🚀 **Procesamiento rápido**: Usa OpenAI Whisper para transcripciones precisas
- 📱 **Integración con Telegram**: Bot nativo de Telegram
- 🔒 **Seguro**: No almacena archivos permanentemente
- 🌍 **Soporte para español**: Optimizado para transcripciones en español

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd Proyecto-Todista
git checkout audio-transcription-only
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Copia `config.env.example` a `config.env` y configura:

```env
TELEGRAM_TOKEN=tu_token_de_telegram
OPENAI_API_KEY=tu_api_key_de_openai
```

## 🚀 Uso

### Ejecutar el bot
```bash
python main.py
```

### Comandos disponibles
- `/start` - Mensaje de bienvenida
- `/help` - Ayuda detallada

### Cómo usar
1. Envía una nota de voz al bot
2. El bot transcribirá automáticamente el audio
3. Recibirás el texto transcrito

## 📋 Requisitos

- Python 3.8+
- Token de bot de Telegram
- API Key de OpenAI (con créditos)

## 🔧 Configuración

### Obtener Token de Telegram
1. Habla con @BotFather en Telegram
2. Crea un nuevo bot con `/newbot`
3. Copia el token proporcionado

### Obtener API Key de OpenAI
1. Ve a [OpenAI Platform](https://platform.openai.com/)
2. Crea una cuenta o inicia sesión
3. Genera una nueva API key
4. Asegúrate de tener créditos disponibles

## 📁 Estructura del Proyecto

```
Proyecto-Todista/
├── main.py                    # Bot principal
├── requirements.txt           # Dependencias
├── config.env.example        # Ejemplo de configuración
├── README_AUDIO_TRANSCRIPTION.md  # Este archivo
└── .gitignore               # Archivos ignorados
```

## 🔍 Funcionalidades

### Transcripción de Audio
- Soporta notas de voz de hasta 5 minutos
- Archivos de hasta 50MB
- Transcripción en español
- Manejo de errores robusto

### Límites
- **Duración máxima**: 5 minutos
- **Tamaño máximo**: 50MB
- **Idioma**: Español (configurable)

## 🚨 Solución de Problemas

### Error: "Faltan variables de entorno"
- Verifica que `config.env` existe
- Asegúrate de que las variables estén configuradas

### Error: "No se pudo transcribir el audio"
- Verifica que el audio sea claro
- Asegúrate de que contenga habla
- Verifica tu conexión a internet

### Error: "Error al procesar el audio"
- Verifica que tengas créditos en OpenAI
- Revisa tu conexión a internet
- Verifica que la API key sea válida

## 🔄 Diferencias con la Versión Completa

Esta rama (`audio-transcription-only`) se diferencia de la rama principal en:

| Característica | Versión Completa | Versión Transcripción |
|----------------|------------------|----------------------|
| Transcripción de audio | ✅ | ✅ |
| Integración con Todoist | ✅ | ❌ |
| Análisis con Gemini | ✅ | ❌ |
| Gestión de tareas | ✅ | ❌ |
| Edición de tareas | ✅ | ❌ |
| Comandos avanzados | ✅ | ❌ |

## 📝 Licencia

Este proyecto está bajo la misma licencia que el proyecto principal.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de solución de problemas
2. Verifica los logs del bot
3. Asegúrate de que todas las configuraciones sean correctas

---

**Nota**: Esta es una versión simplificada enfocada únicamente en transcripción de audio. Para funcionalidades completas de gestión de tareas, usa la rama principal. 