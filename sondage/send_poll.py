from telegram import Update, Poll
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import asyncio, sqlite3, csv
from asgiref.sync import sync_to_async
from bots.models import Utilisateur



# Fonction pour envoyer le sondage à tous les utilisateurs
async def send_poll_to_all_users(context: ContextTypes.DEFAULT_TYPE,poll_data):
    users =  await sync_to_async(lambda: list(Utilisateur.objects.all()))() 

    for user in users: 
        try:
            await context.bot.send_poll(
                chat_id=user.telegram_user_id,
                question=poll_data['question'],
                options=poll_data['options'],
                is_anonymous=False,
                allows_multiple_answers=False
            )
        except Exception as e:
            print(f"Erreur lors de l'envoi du sondage à l'utilisateur {user[0]} : {e}")