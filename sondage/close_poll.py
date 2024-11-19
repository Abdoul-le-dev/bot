
from telegram import Update, Poll
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import asyncio, sqlite3, csv
from sondage.export_result import export_results_to_admin

# Fonction pour envoyer un message de fin du sondage et exporter le fichier pour admin
async def close_poll_after_duration(context: ContextTypes.DEFAULT_TYPE, chat_id, message_id, duration_days,poll_data,ADMIN_IDS):
    await asyncio.sleep(duration_days * 24 * 60 * 60)  
    await context.bot.stop_poll(chat_id=chat_id, message_id=message_id)
    await context.bot.send_message(chat_id=chat_id, text="Le sondage est maintenant clos. Merci pour votre participation !")
    await export_results_to_admin(context,poll_data,ADMIN_IDS)