import sqlite3
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from reminder.send_users import send_reminder

ADMIN_IDS = {1150156856, 7171212138 }  

# États de la conversation pour l'admin
SET_CONTENT, SET_DATETIME = range(2)

# Initialise le planificateur de rappels
scheduler = AsyncIOScheduler()
scheduler.start()

# Dictionnaire pour stocker les informations du rappel temporairement
reminder_data = {}

# Commande pour démarrer la configuration d'un rappel par l'admin
async def start_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Seuls les administrateurs peuvent créer des rappels.")
        return ConversationHandler.END

    await update.message.reply_text("Veuillez entrer le contenu du rappel :")
    return SET_CONTENT

async def set_reminder_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reminder_data['content'] = update.message.text
    await update.message.reply_text("Entrez la date et l'heure du rappel (format : AAAA-MM-JJ HH:MM) Ex: 2024-10-21 12:30 :")
    return SET_DATETIME

async def set_reminder_datetime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    datetime_str = update.message.text
    try:
        reminder_time = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        reminder_data['time'] = reminder_time
    except ValueError:
        await update.message.reply_text("Format de date invalide. Veuillez entrer la date et l'heure au format AAAA-MM-JJ HH:MM. Ex: 2024-10-21 12:30")
        return SET_DATETIME

    scheduler.add_job(
        send_reminder,
        trigger='date',
        run_date=reminder_data['time'],
        args=[context, reminder_data['content']]
    )

    await update.message.reply_text(f"Rappel configuré pour le {reminder_time.strftime('%Y-%m-%d %H:%M')}.")
    return ConversationHandler.END



# Handler de rappel pour l'administrateur
reminder_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("rappel", start_reminder)],
    states={
        SET_CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_reminder_content)],
        SET_DATETIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_reminder_datetime)],
    },
    fallbacks=[]
)



