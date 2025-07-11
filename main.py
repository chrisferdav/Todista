import logging
import os
import tempfile
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('config.env')

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuración de APIs desde variables de entorno
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Verificar que las variables estén configuradas
if not all([TELEGRAM_TOKEN, OPENAI_API_KEY]):
    logger.error("❌ Faltan variables de entorno requeridas. Verifica config.env")
    exit(1)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /start"""
    user = update.effective_user
    await update.message.reply_html(
        f"¡Hola {user.mention_html()}! 👋\n\n"
        "Soy tu <b>Bot de Transcripción de Audio</b> 🤖\n\n"
        "Convierte tus notas de voz en texto transcrito.\n\n"
        "📋 <b>Comandos disponibles:</b>\n"
        "• /start - Mensaje de bienvenida\n"
        "• /help - Ver ayuda detallada\n\n"
        "🎵 <b>Envía una nota de voz</b> para transcribirla a texto."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /help"""
    help_text = """
🤖 <b>Bot de Transcripción de Audio - Ayuda</b>

<b>¿Qué hace este bot?</b>
Convierte tus notas de voz en texto transcrito usando OpenAI Whisper.

<b>🔄 Flujo de Procesamiento:</b>
1. 📥 Recibe tu nota de voz
2. 🎤 Transcribe con OpenAI Whisper
3. 📝 Te envía el texto transcrito

<b>📝 Cómo usar:</b>
• <b>Envía una nota de voz</b> desde Telegram
• El bot procesará automáticamente
• Recibirás la transcripción en texto

<b>💡 Ejemplos de uso:</b>
• <b>Nota de voz:</b> "Recordar comprar leche mañana"
• <b>Nota de voz:</b> "Tengo que terminar el proyecto para el viernes"
• <b>Nota de voz:</b> "Llamar al médico el lunes por la mañana"

<b>⚙️ Configuración requerida:</b>
• ✅ Telegram Bot Token
• ✅ OpenAI API Key (con créditos)

<b>📋 Comandos:</b>
• /start - Mensaje de bienvenida
• /help - Esta ayuda

<b>🔧 Soporte:</b>
Si tienes problemas, verifica:
• Conexión a internet
• API keys configuradas
• Créditos en OpenAI
"""
    
    await update.message.reply_html(help_text)

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja mensajes de voz y los transcribe"""
    voice = update.message.voice
    
    if voice:
        file_id = voice.file_id
        duration = voice.duration
        file_size = voice.file_size
        
        # Verificar límites
        if duration > 300:  # 5 minutos
            await update.message.reply_text("❌ El audio es demasiado largo. Máximo 5 minutos.")
            return
        
        if file_size > 50 * 1024 * 1024:  # 50MB
            await update.message.reply_text("❌ El archivo es demasiado grande. Máximo 50MB.")
            return
        
        await process_voice_note(update, context, voice)
    else:
        await update.message.reply_text("❌ No se detectó un archivo de voz válido.")

async def process_voice_note(update: Update, context: ContextTypes.DEFAULT_TYPE, voice) -> None:
    """Procesa la nota de voz usando OpenAI Whisper para transcripción"""
    try:
        # Descargar el archivo de audio
        file = await context.bot.get_file(voice.file_id)
        
        # Crear archivo temporal para guardar el audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
            temp_file_path = temp_file.name
        
        # Descargar el archivo
        await file.download_to_drive(temp_file_path)
        
        await update.message.reply_text("🎤 Transcribiendo audio con Whisper...")
        
        # Transcribir usando OpenAI Whisper
        with open(temp_file_path, 'rb') as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="es"  # Especificar español
            )
        
        # Obtener el texto transcrito
        transcribed_text = transcript.text
        
        # Limpiar archivo temporal
        os.unlink(temp_file_path)
        
        if transcribed_text and transcribed_text.strip():
            # Enviar transcripción
            response_text = f"📝 <b>Transcripción:</b>\n\n{transcribed_text}"
            await update.message.reply_html(response_text)
            
            logger.info(f"✅ Transcripción exitosa para usuario {update.effective_user.id}")
        else:
            await update.message.reply_text(
                "❌ No se pudo transcribir el audio. "
                "Asegúrate de que el audio sea claro y contenga habla."
            )
            
    except Exception as e:
        logger.error(f"❌ Error en transcripción: {str(e)}")
        await update.message.reply_text(
            "❌ Error al procesar el audio. "
            "Verifica tu conexión a internet y que tengas créditos en OpenAI."
        )
        
        # Limpiar archivo temporal si existe
        try:
            if 'temp_file_path' in locals():
                os.unlink(temp_file_path)
        except:
            pass

async def handle_audio_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja archivos de audio (no notas de voz)"""
    await update.message.reply_text(
        "📁 Archivo de audio recibido.\n"
        "Por favor, envía una nota de voz para transcripción."
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja errores del bot"""
    logger.error(f"❌ Error en el bot: {context.error}")
    
    if update and hasattr(update, 'message') and update.message:
        await update.message.reply_text(
            "❌ Ocurrió un error inesperado. "
            "Por favor, intenta de nuevo más tarde."
        )

def main() -> None:
    """Función principal del bot"""
    # Crear aplicación
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Agregar handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Handler para notas de voz
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    
    # Handler para archivos de audio (opcional)
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio_message))
    
    # Handler de errores
    application.add_error_handler(error_handler)
    
    # Iniciar el bot
    logger.info("🤖 Bot de Transcripción iniciado...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
