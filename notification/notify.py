import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from asgiref.sync import sync_to_async
from bots.models import Utilisateur

ADMIN_IDS = {1150156856, 7171212138 }  

# États de la conversation
NOTIFY = range(1)

# Commande pour démarrer la notification à tous les utilisateurs
async def start_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Seuls les administrateurs peuvent envoyer des notifications.")
        return ConversationHandler.END

    await update.message.reply_text("Tapez le message que vous souhaitez envoyer à tous les utilisateurs :")
    return NOTIFY

# Fonction pour envoyer la notification à tous les utilisateurs
async def send_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    users =  await sync_to_async(lambda: list(Utilisateur.objects.all()))()
    failed_users = []
    for user in users:
        try:
           await context.bot.send_message(chat_id=user.telegram_user_id, text=message)
        except Exception as e:
            print(f"Erreur lors de l'envoi à l'utilisateur {user[0]} : {e}")
            failed_users.append(user[0])

    if not failed_users:
        await update.message.reply_text("Le message a été envoyé à tous les utilisateurs avec succès.")
    else:
        await update.message.reply_text(f"Le message n'a pas pu être envoyé à certains utilisateurs : {failed_users}")

    return ConversationHandler.END



# Handler de notification pour l'administrateur
notify_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("notifier", start_notify)],
    states={
        NOTIFY: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_notification)],
    },
    fallbacks=[]
)

