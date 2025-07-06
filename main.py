import logging
import os
import tempfile
import json
from datetime import datetime, timedelta
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import openai
import google.generativeai as genai
from todoist_api_python.api import TodoistAPI
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
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
TODOIST_API_TOKEN = os.getenv('TODOIST_API_TOKEN')

# Configurar zona horaria
TIMEZONE = pytz.timezone('America/Bogota')  # UTM-5

def get_current_date():
    """Obtiene la fecha actual en formato dd-mm-yyyy en UTM-5"""
    return datetime.now(TIMEZONE).strftime('%d-%m-%Y')

def get_current_date_iso():
    """Obtiene la fecha actual en formato ISO para Todoist en UTM-5"""
    return datetime.now(TIMEZONE).strftime('%Y-%m-%d')

# Verificar que todas las variables estén configuradas
if not all([TELEGRAM_TOKEN, OPENAI_API_KEY, GEMINI_API_KEY]):
    logger.error("❌ Faltan variables de entorno requeridas. Verifica config.env")
    exit(1)

if not TODOIST_API_TOKEN or TODOIST_API_TOKEN == "TU_TODOIST_API_TOKEN_AQUI":
    logger.warning("⚠️ TODOIST_API_TOKEN no configurado. Las tareas no se crearán en Todoist.")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /start"""
    user = update.effective_user
    await update.message.reply_html(
        f"¡Hola {user.mention_html()}! 👋\n\n"
        "Soy tu <b>Bot de Notas de Voz Inteligente</b> 🤖\n\n"
        "Convierte tus notas de voz en tareas organizadas automáticamente.\n\n"
        "📋 <b>Comandos disponibles:</b>\n"
        "• /start - Mensaje de bienvenida\n"
        "• /help - Ver ayuda detallada\n"
        "• /tasks [fecha] - Ver tareas de un día\n\n"
        "🎵 <b>Envía una nota de voz</b> o <b>escribe texto</b> para crear tareas."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /help"""
    help_text = """
🤖 <b>Bot de Notas de Voz - Ayuda Completa</b>

<b>¿Qué hace este bot?</b>
Convierte tus notas de voz en tareas organizadas automáticamente usando IA.

<b>🔄 Flujo de Procesamiento:</b>
1. 📥 Recibe tu nota de voz
2. 🎤 Transcribe con OpenAI Whisper
3. 🧠 Analiza con Google Gemini
4. 📋 Estructura las tareas
5. 📱 Crea tareas en Todoist
6. 🔗 Te envía enlaces directos

<b>📝 Cómo usar:</b>
• <b>Envía una nota de voz</b> con tareas o recordatorios
• <b>Escribe texto</b> directamente con tareas
• El bot procesará automáticamente
• Recibirás transcripción + tareas estructuradas
• Las tareas se crearán en tu Todoist

<b>💡 Ejemplos de uso:</b>
• <b>Nota de voz:</b> "Recordar comprar leche mañana, alta prioridad"
• <b>Texto:</b> "Tengo que terminar el proyecto para el viernes"
• <b>Texto:</b> "Llamar al médico el lunes por la mañana"

<b>⚙️ Configuración requerida:</b>
• ✅ Telegram Bot Token
• ✅ OpenAI API Key (con créditos)
• ✅ Google Gemini API Key
• ✅ Todoist API Token

<b>📋 Comandos:</b>
• /start - Mensaje de bienvenida
• /help - Esta ayuda
• /tasks [fecha] - Ver tareas de un día específico

<b>🔧 Soporte:</b>
Si tienes problemas, verifica:
• Conexión a internet
• API keys configuradas
• Créditos en OpenAI
• Token de Todoist válido
"""
    
    await update.message.reply_html(help_text)

async def tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /tasks para mostrar tareas de un día específico"""
    if not TODOIST_API_TOKEN or TODOIST_API_TOKEN == "TU_TODOIST_API_TOKEN_AQUI":
        await update.message.reply_text("❌ Token de Todoist no configurado.")
        return
    
    # Obtener fecha del comando (opcional)
    args = context.args
    target_date = None
    
    if args:
        date_arg = " ".join(args)
        # Procesar diferentes formatos de fecha
        if date_arg.lower() in ['hoy', 'today']:
            target_date = get_current_date_iso()
        elif date_arg.lower() in ['mañana', 'tomorrow']:
            target_date = (datetime.now(TIMEZONE) + timedelta(days=1)).strftime('%Y-%m-%d')
        elif date_arg.lower() in ['ayer', 'yesterday']:
            target_date = (datetime.now(TIMEZONE) - timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            # Intentar parsear fecha específica
            try:
                # Priorizar formato dd-mm-yyyy
                for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d/%m/%y']:
                    try:
                        parsed_date = datetime.strptime(date_arg, fmt)
                        target_date = parsed_date.strftime('%Y-%m-%d')
                        break
                    except ValueError:
                        continue
                
                if not target_date:
                    await update.message.reply_text(
                        "❌ Formato de fecha no reconocido.\n\n"
                        "Formatos válidos:\n"
                        "• /tasks hoy\n"
                        "• /tasks mañana\n"
                        "• /tasks 2024-10-23\n"
                        "• /tasks 23/10/2024"
                    )
                    return
            except:
                await update.message.reply_text(
                    "❌ Formato de fecha no reconocido.\n\n"
                    "Formatos válidos:\n"
                    "• /tasks hoy\n"
                    "• /tasks mañana\n"
                    "• /tasks 2024-10-23\n"
                    "• /tasks 23/10/2024"
                )
                return
    else:
        # Si no se especifica fecha, usar hoy
        target_date = get_current_date_iso()
    
    try:
        api = TodoistAPI(TODOIST_API_TOKEN)
        
        # Obtener tareas
        tasks = api.get_tasks()
        
        # Filtrar tareas por fecha
        filtered_tasks = []
        for task in tasks:
            if task.due and task.due.date == target_date:
                filtered_tasks.append(task)
        
        if not filtered_tasks:
            # Convertir fecha ISO a formato dd-mm-yyyy para mostrar
            display_date = datetime.strptime(target_date, '%Y-%m-%d').strftime('%d-%m-%Y')
            await update.message.reply_text(
                f"📅 <b>No hay tareas para el {display_date}</b>\n\n"
                "¡Disfruta tu día libre! 🎉",
                parse_mode='HTML'
            )
            return
        
        # Construir respuesta
        display_date = datetime.strptime(target_date, '%Y-%m-%d').strftime('%d-%m-%Y')
        response_text = f"📅 <b>Tareas para el {display_date}:</b>\n\n"
        
        for i, task in enumerate(filtered_tasks, 1):
            response_text += f"{i}. <b>{task.content}</b>\n"
            if task.description:
                response_text += f"   📄 {task.description}\n"
            if task.priority:
                priority_text = {1: "Baja", 2: "Media", 3: "Alta", 4: "Muy Alta"}.get(task.priority, "Sin prioridad")
                response_text += f"   ⚡ Prioridad: {priority_text}\n"
            if task.project_id:
                try:
                    project = api.get_project(task.project_id)
                    response_text += f"   📁 Proyecto: {project.name}\n"
                except:
                    pass
            response_text += f"   🔗 <a href='https://todoist.com/app/task/{task.id}'>Ver en Todoist</a>\n\n"
        
        response_text += f"📊 <b>Total: {len(filtered_tasks)} tareas</b>"
        
        await update.message.reply_text(response_text, parse_mode='HTML', disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"Error obteniendo tareas: {str(e)}")
        await update.message.reply_text(
            f"❌ Error al obtener tareas: {str(e)}\n\n"
            "Verifica que tu token de Todoist sea válido."
        )

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja las notas de voz recibidas"""
    voice = update.message.voice
    
    if voice:
        # Información de la nota de voz
        file_id = voice.file_id
        duration = voice.duration
        file_size = voice.file_size
        
        await update.message.reply_text(
            f"🎵 Nota de voz recibida!\n\n"
            f"📊 Información:\n"
            f"• Duración: {duration} segundos\n"
            f"• Tamaño: {file_size} bytes\n"
            f"• ID del archivo: {file_id}\n\n"
            f"Procesando tu nota de voz..."
        )
        
        # Aquí puedes agregar la lógica para procesar la nota de voz
        # Por ejemplo: transcribir, guardar, analizar, etc.
        await process_voice_note(update, context, voice)
    else:
        await update.message.reply_text("No se pudo procesar la nota de voz.")

async def process_voice_note(update: Update, context: ContextTypes.DEFAULT_TYPE, voice) -> None:
    """Procesa la nota de voz usando OpenAI Whisper para transcripción"""
    try:
        # Configurar OpenAI
        openai.api_key = OPENAI_API_KEY
        
        # Descargar el archivo de audio
        await update.message.reply_text("📥 Descargando nota de voz...")
        
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
                response_format="text"
            )
        
        # Limpiar archivo temporal
        os.unlink(temp_file_path)
        
        if transcript and transcript.strip():
            # Enviar transcripción al usuario
            await update.message.reply_text(
                f"📝 **Transcripción:**\n\n{transcript.strip()}\n\n"
                f"🔄 Procesando con Gemini..."
            )
            
            # Procesar texto con Gemini
            gemini_result = await process_text_with_gemini(transcript.strip())
            
            # Construir respuesta con el análisis
            response_text = f"📝 <b>Transcripción:</b>\n\n{transcript.strip()}\n\n"
            
            if gemini_result.get("tasks"):
                response_text += "📋 <b>Tareas Identificadas:</b>\n\n"
                
                # Guardar tareas en el contexto para confirmación posterior
                context.user_data['pending_tasks'] = gemini_result["tasks"]
                
                for i, task in enumerate(gemini_result["tasks"], 1):
                    response_text += f"{i}. <b>{task.get('title', 'Sin título')}</b>\n"
                    if task.get('description'):
                        response_text += f"   📄 {task['description']}\n"
                    if task.get('priority'):
                        response_text += f"   ⚡ Prioridad: {task['priority']}\n"
                    if task.get('due_date'):
                        response_text += f"   📅 Fecha: {task['due_date']}\n"
                    if task.get('category'):
                        response_text += f"   🏷️ Categoría: {task['category']}\n"
                    response_text += "\n"
                
                response_text += "🔘 <b>Usa los botones para confirmar o editar las tareas:</b>"
                
                # Crear botones interactivos
                keyboard = create_task_confirmation_keyboard(gemini_result["tasks"], update.effective_user.id)
                
                await update.message.reply_text(response_text, parse_mode='HTML', reply_markup=keyboard)
                        
            else:
                response_text += "📋 <b>Análisis:</b>\n\n"
                response_text += f"{gemini_result.get('summary', 'No se pudo analizar el texto')}\n\n"
                response_text += "✅ Procesamiento completado exitosamente!"
                
                await update.message.reply_text(response_text, parse_mode='HTML')
            
            logger.info(f"Procesamiento completo exitoso para usuario {update.effective_user.id}")
            
        else:
            await update.message.reply_text(
                "❌ No se pudo transcribir el audio. "
                "Asegúrate de que el audio sea claro y contenga habla."
            )
            
    except Exception as e:
        logger.error(f"Error procesando nota de voz: {str(e)}")
        await update.message.reply_text(
            f"❌ Error al procesar la nota de voz: {str(e)}\n\n"
            "Verifica que tu API key de OpenAI sea válida y tengas créditos disponibles."
        )

async def process_text_with_gemini(text: str) -> dict:
    """Procesa el texto transcrito con Google Gemini para estructurar tareas"""
    try:
        # Configurar Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Prompt para estructurar tareas
        prompt = f"""
        Analiza el siguiente texto y extrae las tareas o acciones mencionadas. 
        Devuelve la respuesta en formato JSON con la siguiente estructura:
        
        {{
            "tasks": [
                {{
                    "title": "Título de la tarea",
                    "description": "Descripción detallada",
                    "priority": "alta/media/baja",
                    "due_date": "YYYY-MM-DD" (si se menciona),
                    "category": "trabajo/personal/estudio/etc"
                }}
            ],
            "summary": "Resumen general del texto"
        }}
        
        Texto a analizar: "{text}"
        
        Si no hay tareas específicas, devuelve un JSON con tasks vacío y un summary del texto.
        """
        
        response = model.generate_content(prompt)
        
        # Intentar parsear la respuesta JSON
        try:
            # Limpiar la respuesta para extraer solo el JSON
            response_text = response.text.strip()
            
            # Si la respuesta está envuelta en ```json ... ```, extraer solo el contenido
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Remover comentarios de JavaScript (// ...)
            import re
            response_text = re.sub(r'//.*$', '', response_text, flags=re.MULTILINE)
            
            # Limpiar líneas vacías extra
            response_text = '\n'.join(line for line in response_text.split('\n') if line.strip())
                
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {e}")
            logger.error(f"Response text: {response_text}")
            # Si no es JSON válido, crear una estructura básica
            return {
                "tasks": [],
                "summary": response.text,
                "raw_response": response.text
            }
            
    except Exception as e:
        logger.error(f"Error procesando texto con Gemini: {str(e)}")
        return {
            "tasks": [],
            "summary": f"Error al procesar con Gemini: {str(e)}",
            "error": str(e)
        }

async def create_todoist_task(task_data: dict) -> dict:
    """Crea una tarea en Todoist basada en los datos estructurados"""
    try:
        api = TodoistAPI(TODOIST_API_TOKEN)
        
        # Preparar datos de la tarea
        content = task_data.get('title', 'Tarea sin título') or 'Tarea sin título'
        description = task_data.get('description', '') or ''
        
        # Procesar fecha
        due_date = None
        due_string = task_data.get('due_date', '')
        if due_string and isinstance(due_string, str):
            if due_string.lower() == 'mañana':
                due_date = (datetime.now(TIMEZONE) + timedelta(days=1)).strftime('%Y-%m-%d')
            elif due_string.lower() == 'hoy':
                due_date = get_current_date_iso()
            elif due_string.lower() == 'próxima semana':
                due_date = (datetime.now(TIMEZONE) + timedelta(days=7)).strftime('%Y-%m-%d')
            else:
                # Intentar parsear fecha específica en formato dd-mm-yyyy
                try:
                    parsed_date = datetime.strptime(due_string, '%d-%m-%Y')
                    due_date = parsed_date.strftime('%Y-%m-%d')
                except:
                    # Intentar otros formatos como respaldo
                    try:
                        due_date = datetime.strptime(due_string, '%Y-%m-%d').strftime('%Y-%m-%d')
                    except:
                        due_date = None
        
        # Procesar prioridad
        priority_map = {
            'alta': 4,
            'media': 3,
            'baja': 2,
            'muy alta': 4,
            'muy baja': 1
        }
        priority_str = task_data.get('priority', '')
        if priority_str and isinstance(priority_str, str):
            priority = priority_map.get(priority_str.lower(), 1)
        else:
            priority = 1
        
        # Log para debugging
        logger.info(f"Creando tarea: content='{content}', description='{description}', due_date='{due_date}', priority={priority}")
        
        # Crear la tarea
        task = api.add_task(
            content=content,
            description=description,
            due_date=due_date,
            priority=priority
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "task_url": f"https://todoist.com/app/task/{task.id}",
            "message": f"✅ Tarea creada exitosamente en Todoist"
        }
        
    except Exception as e:
        logger.error(f"Error creando tarea en Todoist: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"❌ Error al crear tarea en Todoist: {str(e)}"
        }

def create_task_confirmation_keyboard(tasks_data: list, user_id: int) -> InlineKeyboardMarkup:
    """Crea botones interactivos para confirmar tareas"""
    keyboard = []
    
    for i, task in enumerate(tasks_data):
        task_title = task.get('title', 'Sin título')[:30]  # Limitar longitud
        keyboard.append([
            InlineKeyboardButton(
                f"✅ Confirmar: {task_title}",
                callback_data=f"confirm_{user_id}_{i}"
            )
        ])
        keyboard.append([
            InlineKeyboardButton(
                f"✏️ Editar: {task_title}",
                callback_data=f"edit_{user_id}_{i}"
            )
        ])
    
    # Botones de acción general
    keyboard.append([
        InlineKeyboardButton("✅ Confirmar Todas", callback_data=f"confirm_all_{user_id}"),
        InlineKeyboardButton("❌ Cancelar Todas", callback_data=f"cancel_all_{user_id}")
    ])
    
    return InlineKeyboardMarkup(keyboard)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja las interacciones con botones"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    # Extraer información del callback_data
    if data.startswith("confirm_"):
        if data.startswith("confirm_all_"):
            # Confirmar todas las tareas
            await confirm_all_tasks(update, context, user_id)
        else:
            # Confirmar tarea específica
            task_index = int(data.split("_")[2])
            await confirm_single_task(update, context, user_id, task_index)
    
    elif data.startswith("edit_"):
        # Editar tarea específica
        task_index = int(data.split("_")[2])
        await edit_task(update, context, user_id, task_index)
    
    elif data.startswith("cancel_all_"):
        # Cancelar todas las tareas
        await cancel_all_tasks(update, context, user_id)
    
    elif data.startswith("cancel_edit_"):
        # Cancelar edición
        await cancel_edit(update, context, user_id)
    
    elif data.startswith("keep_original_"):
        # Mantener tarea original
        task_index = int(data.split("_")[3])
        await keep_original_task(update, context, user_id, task_index)

async def confirm_all_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Confirma todas las tareas pendientes"""
    query = update.callback_query
    
    # Obtener tareas del contexto
    tasks_data = context.user_data.get('pending_tasks', [])
    
    if not tasks_data:
        await query.edit_message_text("❌ No hay tareas pendientes para confirmar.")
        return
    
    # Crear todas las tareas en Todoist
    results = []
    for task in tasks_data:
        result = await create_todoist_task(task)
        results.append(result)
    
    # Construir respuesta
    response_text = "📱 <b>Estado en Todoist:</b>\n\n"
    for i, result in enumerate(results, 1):
        if result["success"]:
            response_text += f"{i}. ✅ {result['message']}\n"
            response_text += f"   🔗 <a href='{result['task_url']}'>Ver tarea</a>\n\n"
        else:
            response_text += f"{i}. ❌ {result['message']}\n\n"
    
    response_text += "✅ <b>Todas las tareas procesadas!</b>"
    
    await query.edit_message_text(response_text, parse_mode='HTML', disable_web_page_preview=True)
    
    # Limpiar tareas pendientes
    context.user_data.pop('pending_tasks', None)

async def confirm_single_task(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, task_index: int) -> None:
    """Confirma una tarea específica"""
    query = update.callback_query
    
    tasks_data = context.user_data.get('pending_tasks', [])
    
    if task_index >= len(tasks_data):
        await query.edit_message_text("❌ Tarea no encontrada.")
        return
    
    task = tasks_data[task_index]
    result = await create_todoist_task(task)
    
    if result["success"]:
        response_text = f"✅ <b>Tarea creada exitosamente!</b>\n\n"
        response_text += f"📋 <b>{task.get('title', 'Sin título')}</b>\n"
        response_text += f"🔗 <a href='{result['task_url']}'>Ver en Todoist</a>"
    else:
        response_text = f"❌ <b>Error al crear tarea:</b>\n{result['message']}"
    
    await query.edit_message_text(response_text, parse_mode='HTML', disable_web_page_preview=True)

async def edit_task(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, task_index: int) -> None:
    """Permite editar una tarea específica"""
    query = update.callback_query
    
    tasks_data = context.user_data.get('pending_tasks', [])
    
    if task_index >= len(tasks_data):
        await query.edit_message_text("❌ Tarea no encontrada.")
        return
    
    task = tasks_data[task_index]
    
    # Guardar información de edición en el contexto
    context.user_data['editing_task'] = {
        'index': task_index,
        'original_task': task.copy()
    }
    
    # Mostrar la tarea actual y solicitar edición
    edit_text = f"✏️ <b>Editando tarea:</b>\n\n"
    edit_text += f"📋 <b>Título:</b> {task.get('title', 'Sin título')}\n"
    edit_text += f"📄 <b>Descripción:</b> {task.get('description', 'Sin descripción')}\n"
    edit_text += f"⚡ <b>Prioridad:</b> {task.get('priority', 'Sin prioridad')}\n"
    edit_text += f"📅 <b>Fecha:</b> {task.get('due_date', 'Sin fecha')}\n"
    edit_text += f"🏷️ <b>Categoría:</b> {task.get('category', 'Sin categoría')}\n\n"
    edit_text += "💬 <b>Escribe tu corrección:</b>\n"
    edit_text += "Ejemplo: 'Cambiar título a: Reunión importante, prioridad alta, fecha mañana'"
    
    # Crear botones para la edición
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancelar Edición", callback_data=f"cancel_edit_{user_id}")],
        [InlineKeyboardButton("✅ Mantener Original", callback_data=f"keep_original_{user_id}_{task_index}")]
    ])
    
    await query.edit_message_text(edit_text, parse_mode='HTML', reply_markup=keyboard)

async def handle_text_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja la edición de texto para tareas y creación de tareas via texto"""
    text = update.message.text
    
    # Si estamos en modo edición
    if 'editing_task' in context.user_data:
        await handle_task_editing(update, context, text)
    else:
        # Crear tareas via texto
        await handle_text_task_creation(update, context, text)

async def handle_task_editing(update: Update, context: ContextTypes.DEFAULT_TYPE, edit_text: str) -> None:
    """Maneja la edición específica de una tarea"""
    editing_info = context.user_data['editing_task']
    task_index = editing_info['index']
    original_task = editing_info['original_task']
    
    # Procesar el texto de edición con Gemini
    gemini_result = await process_text_with_gemini(edit_text)
    
    if gemini_result.get("tasks"):
        # Usar la primera tarea del resultado como edición
        edited_task = gemini_result["tasks"][0]
        
        # Actualizar la tarea en el contexto
        tasks_data = context.user_data.get('pending_tasks', [])
        if task_index < len(tasks_data):
            tasks_data[task_index] = edited_task
            
            # Mostrar confirmación de edición
            response_text = f"✅ <b>Tarea editada exitosamente!</b>\n\n"
            response_text += f"📋 <b>Nuevo título:</b> {edited_task.get('title', 'Sin título')}\n"
            response_text += f"📄 <b>Nueva descripción:</b> {edited_task.get('description', 'Sin descripción')}\n"
            response_text += f"⚡ <b>Nueva prioridad:</b> {edited_task.get('priority', 'Sin prioridad')}\n"
            response_text += f"📅 <b>Nueva fecha:</b> {edited_task.get('due_date', 'Sin fecha')}\n"
            response_text += f"🏷️ <b>Nueva categoría:</b> {edited_task.get('category', 'Sin categoría')}\n\n"
            response_text += "🔘 <b>Usa los botones para confirmar:</b>"
            
            # Crear botones actualizados
            keyboard = create_task_confirmation_keyboard(tasks_data, update.effective_user.id)
            
            await update.message.reply_text(response_text, parse_mode='HTML', reply_markup=keyboard)
        else:
            await update.message.reply_text("❌ Error: Tarea no encontrada para editar.")
    else:
        await update.message.reply_text("❌ No se pudo procesar la edición. Intenta ser más específico.")
    
    # Limpiar modo edición
    context.user_data.pop('editing_task', None)

async def handle_text_task_creation(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    """Maneja la creación de tareas via texto"""
    # Procesar el texto con Gemini
    gemini_result = await process_text_with_gemini(text)
    
    if gemini_result.get("tasks"):
        # Guardar tareas en el contexto para confirmación posterior
        context.user_data['pending_tasks'] = gemini_result["tasks"]
        
        # Construir respuesta
        response_text = f"📝 <b>Texto procesado:</b>\n\n{text}\n\n"
        response_text += "📋 <b>Tareas Identificadas:</b>\n\n"
        
        for i, task in enumerate(gemini_result["tasks"], 1):
            response_text += f"{i}. <b>{task.get('title', 'Sin título')}</b>\n"
            if task.get('description'):
                response_text += f"   📄 {task['description']}\n"
            if task.get('priority'):
                response_text += f"   ⚡ Prioridad: {task['priority']}\n"
            if task.get('due_date'):
                response_text += f"   📅 Fecha: {task['due_date']}\n"
            if task.get('category'):
                response_text += f"   🏷️ Categoría: {task['category']}\n"
            response_text += "\n"
        
        response_text += "🔘 <b>Usa los botones para confirmar o editar las tareas:</b>"
        
        # Crear botones interactivos
        keyboard = create_task_confirmation_keyboard(gemini_result["tasks"], update.effective_user.id)
        
        await update.message.reply_text(response_text, parse_mode='HTML', reply_markup=keyboard)
    else:
        await update.message.reply_text(
            "❌ No se identificaron tareas en el texto.\n\n"
            "💡 <b>Ejemplos de texto válido:</b>\n"
            "• 'Comprar leche mañana, alta prioridad'\n"
            "• 'Terminar proyecto para el viernes'\n"
            "• 'Llamar al médico el lunes por la mañana'",
            parse_mode='HTML'
        )
    
    editing_info = context.user_data['editing_task']
    task_index = editing_info['index']
    original_task = editing_info['original_task']
    
    # Procesar el texto de edición con Gemini
    edit_text = update.message.text
    gemini_result = await process_text_with_gemini(edit_text)
    
    if gemini_result.get("tasks"):
        # Usar la primera tarea del resultado como edición
        edited_task = gemini_result["tasks"][0]
        
        # Actualizar la tarea en el contexto
        tasks_data = context.user_data.get('pending_tasks', [])
        if task_index < len(tasks_data):
            tasks_data[task_index] = edited_task
            
            # Mostrar confirmación de edición
            response_text = f"✅ <b>Tarea editada exitosamente!</b>\n\n"
            response_text += f"📋 <b>Nuevo título:</b> {edited_task.get('title', 'Sin título')}\n"
            response_text += f"📄 <b>Nueva descripción:</b> {edited_task.get('description', 'Sin descripción')}\n"
            response_text += f"⚡ <b>Nueva prioridad:</b> {edited_task.get('priority', 'Sin prioridad')}\n"
            response_text += f"📅 <b>Nueva fecha:</b> {edited_task.get('due_date', 'Sin fecha')}\n"
            response_text += f"🏷️ <b>Nueva categoría:</b> {edited_task.get('category', 'Sin categoría')}\n\n"
            response_text += "🔘 <b>Usa los botones para confirmar:</b>"
            
            # Crear botones actualizados
            keyboard = create_task_confirmation_keyboard(tasks_data, update.effective_user.id)
            
            await update.message.reply_text(response_text, parse_mode='HTML', reply_markup=keyboard)
        else:
            await update.message.reply_text("❌ Error: Tarea no encontrada para editar.")
    else:
        await update.message.reply_text("❌ No se pudo procesar la edición. Intenta ser más específico.")
    
    # Limpiar modo edición
    context.user_data.pop('editing_task', None)

async def cancel_all_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Cancela todas las tareas pendientes"""
    query = update.callback_query
    
    # Limpiar tareas pendientes
    context.user_data.pop('pending_tasks', None)
    
    await query.edit_message_text(
        "❌ <b>Todas las tareas canceladas</b>\n\n"
        "Envía una nueva nota de voz para crear nuevas tareas.",
        parse_mode='HTML'
    )

async def cancel_edit(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Cancela la edición de una tarea"""
    query = update.callback_query
    
    # Limpiar modo edición
    context.user_data.pop('editing_task', None)
    
    # Volver a mostrar las tareas originales
    tasks_data = context.user_data.get('pending_tasks', [])
    if tasks_data:
        response_text = "📋 <b>Tareas Identificadas:</b>\n\n"
        for i, task in enumerate(tasks_data, 1):
            response_text += f"{i}. <b>{task.get('title', 'Sin título')}</b>\n"
            if task.get('description'):
                response_text += f"   📄 {task['description']}\n"
            if task.get('priority'):
                response_text += f"   ⚡ Prioridad: {task['priority']}\n"
            if task.get('due_date'):
                response_text += f"   📅 Fecha: {task['due_date']}\n"
            if task.get('category'):
                response_text += f"   🏷️ Categoría: {task['category']}\n"
            response_text += "\n"
        
        response_text += "🔘 <b>Usa los botones para confirmar o editar las tareas:</b>"
        keyboard = create_task_confirmation_keyboard(tasks_data, user_id)
        
        await query.edit_message_text(response_text, parse_mode='HTML', reply_markup=keyboard)
    else:
        await query.edit_message_text(
            "❌ <b>No hay tareas pendientes</b>\n\n"
            "Envía una nueva nota de voz para crear tareas.",
            parse_mode='HTML'
        )

async def keep_original_task(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, task_index: int) -> None:
    """Mantiene la tarea original sin cambios"""
    query = update.callback_query
    
    # Limpiar modo edición
    context.user_data.pop('editing_task', None)
    
    # Volver a mostrar las tareas originales
    tasks_data = context.user_data.get('pending_tasks', [])
    if tasks_data:
        response_text = "📋 <b>Tareas Identificadas:</b>\n\n"
        for i, task in enumerate(tasks_data, 1):
            response_text += f"{i}. <b>{task.get('title', 'Sin título')}</b>\n"
            if task.get('description'):
                response_text += f"   📄 {task['description']}\n"
            if task.get('priority'):
                response_text += f"   ⚡ Prioridad: {task['priority']}\n"
            if task.get('due_date'):
                response_text += f"   📅 Fecha: {task['due_date']}\n"
            if task.get('category'):
                response_text += f"   🏷️ Categoría: {task['category']}\n"
            response_text += "\n"
        
        response_text += "🔘 <b>Usa los botones para confirmar o editar las tareas:</b>"
        keyboard = create_task_confirmation_keyboard(tasks_data, user_id)
        
        await query.edit_message_text(response_text, parse_mode='HTML', reply_markup=keyboard)
    else:
        await query.edit_message_text(
            "❌ <b>No hay tareas pendientes</b>\n\n"
            "Envía una nueva nota de voz para crear tareas.",
            parse_mode='HTML'
        )

async def handle_audio_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja archivos de audio (no notas de voz)"""
    await update.message.reply_text(
        "📁 Archivo de audio recibido.\n"
        "Para notas de voz, usa la función de grabación de voz de Telegram."
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja errores del bot"""
    logger.error(f"Excepción mientras se manejaba una actualización: {context.error}")

def main() -> None:
    """Función principal del bot"""
    # Crear la aplicación
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Agregar handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("tasks", tasks_command))
    
    # Handler para notas de voz
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    
    # Handler para archivos de audio (opcional)
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio_message))
    
    # Handler para texto (edición de tareas)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_edit))
    
    # Handler para botones interactivos
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Handler de errores
    application.add_error_handler(error_handler)

    # Iniciar el bot
    print("🤖 Bot iniciado. Presiona Ctrl+C para detener.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
