# Bot de Telegram para Notas de Voz

Un bot de Telegram que responde al comando `/start` y maneja notas de voz.

## Características

- ✅ Comando `/start` con mensaje de bienvenida
- ✅ Comando `/help` con ayuda detallada
- 🎵 Manejo de notas de voz
- 🤖 Transcripción automática con OpenAI Whisper
- 🧠 Análisis inteligente con Google Gemini
- 📋 Estructuración automática de tareas
- 🔘 Botones interactivos para confirmar tareas
- 📱 Creación controlada en Todoist
- 🔗 Enlaces directos a las tareas creadas
- 📁 Soporte para archivos de audio
- 🔧 Estructura modular y extensible
- 📝 Logging configurado

## Instalación

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Obtener token del bot:**
   - Habla con [@BotFather](https://t.me/botfather) en Telegram
   - Crea un nuevo bot con `/newbot`
   - Copia el token que te proporciona

3. **Obtener API key de OpenAI:**
   - Ve a [OpenAI API Keys](https://platform.openai.com/api-keys)
   - Crea una nueva API key
   - Asegúrate de tener créditos disponibles para usar Whisper

4. **Obtener API key de Google Gemini:**
   - Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Crea una nueva API key
   - Copia la clave generada

5. **Obtener API token de Todoist:**
   - Ve a [Todoist Settings > Integrations > Developer](https://todoist.com/app/settings/integrations/developer)
   - Crea una nueva API token
   - Copia el token generado

6. **Configurar variables de entorno:**
   - Copia el archivo `config.env.example` a `config.env`
   - Reemplaza los valores con tus API keys reales
   - **IMPORTANTE**: Nunca subas `config.env` a Git (ya está en .gitignore)

## Uso

1. **Ejecutar el bot:**
   ```bash
   python main.py
   ```

2. **En Telegram:**
   - Busca tu bot por su nombre
   - Envía `/start` para comenzar
   - Envía `/help` para ver ayuda detallada
   - Envía notas de voz para que las procese

## Estructura del Código

- `start_command()`: Maneja el comando `/start`
- `help_command()`: Maneja el comando `/help`
- `handle_voice_message()`: Procesa notas de voz recibidas
- `process_voice_note()`: Transcribe y analiza notas de voz
- `process_text_with_gemini()`: Analiza texto con IA
- `create_todoist_task()`: Crea tareas en Todoist
- `handle_audio_message()`: Maneja archivos de audio
- `error_handler()`: Maneja errores del bot

## Flujo de Procesamiento

El bot sigue este flujo para procesar notas de voz:

1. **Recepción**: Recibe la nota de voz de Telegram
2. **Descarga**: Descarga el archivo de audio temporalmente
3. **Transcripción**: Envía el audio a OpenAI Whisper para transcripción
4. **Análisis**: Procesa el texto con Google Gemini para estructurar tareas
5. **Confirmación**: Muestra tareas con botones interactivos
6. **Creación**: Crea tareas en Todoist solo tras confirmación del usuario
7. **Respuesta**: Devuelve transcripción + tareas + enlaces a Todoist
8. **Limpieza**: Elimina el archivo temporal

## Personalización

La función `process_voice_note()` ya está implementada con transcripción Whisper, pero puedes extenderla para:

- Enviar el texto a Google Gemini para análisis
- Crear tareas estructuradas
- Integrar con Todoist
- Guardar en base de datos
- Análisis de sentimientos

## Notas

- El bot usa `python-telegram-bot` versión 20.7, `openai` versión 1.3.0, `google-generativeai` versión 0.3.2 y `todoist-api-python` versión 2.1.3
- Funciona con Python 3.7+
- Requiere conexión a internet para funcionar
- Requiere API key de OpenAI con créditos disponibles para Whisper
- Requiere API key de Google Gemini para análisis de texto
- Requiere API token de Todoist para crear tareas
- Los archivos de audio se procesan temporalmente y se eliminan automáticamente 