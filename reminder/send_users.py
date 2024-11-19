import sqlite3
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from asgiref.sync import sync_to_async
from bots.models import Utilisateur


# Fonction pour envoyer le rappel à tous les utilisateurs
async def send_reminder(context: ContextTypes.DEFAULT_TYPE, content):
    users = await sync_to_async(lambda: list(Utilisateur.objects.all()))()

    for user in users:
        try:
            await context.bot.send_message(chat_id=user.telegram_user_id, text=content)
        except Exception as e:
            print(f"Erreur lors de l'envoi du rappel à l'utilisateur {user[0]} : {e}")
