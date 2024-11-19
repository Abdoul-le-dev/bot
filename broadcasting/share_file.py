import sqlite3
from telegram import Update, InputFile
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from bots.models import Utilisateur
from asgiref.sync import sync_to_async

ADMIN_IDS = {1150156856, 7171212138 }  

awaiting_file = {}

async def start_distribution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_message.from_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Seuls les administrateurs peuvent utiliser cette commande.")
        return

    awaiting_file[user_id] = True
    await update.message.reply_text("Veuillez envoyer le fichier que vous souhaitez distribuer.")


# Fonction pour envoyer un fichier à tous les utilisateurs sauf l'admin expéditeur
async def share_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_message.from_user.id

    if user_id not in ADMIN_IDS or not awaiting_file.get(user_id):
        return 

    message = update.effective_message
    file = None
    if message.document:
        file = message.document
        file_type = "document"
    elif message.audio:
        file = message.audio
        file_type = "audio"
    elif message.video:
        file = message.video
        file_type = "vidéo"
    elif message.voice:
        file = message.voice
        file_type = "voix"
    elif message.photo:
        file = message.photo[-1] 
        file_type = "photo"

    if not file:
        await message.reply_text("Veuillez envoyer un fichier valide (document, audio, vidéo, voix ou photo).")
        return

    file_id = file.file_id
    await message.reply_text(f"{file_type.capitalize()} reçu et en cours de distribution...")
    awaiting_file.pop(user_id)
    
   
    other_users = await sync_to_async(lambda: list(Utilisateur.objects.all()))()  
    for other_user_id in other_users:
        try:
            await context.bot.send_photo(chat_id=other_user_id.telegram_user_id, photo=file_id) if file_type == "photo" else await context.bot.send_document(chat_id=other_user_id[0], document=file_id)
        except Exception as e:
            print(f"Erreur lors de l'envoi à l'utilisateur {other_user_id.telegram_user_id} : {e}")
    
    await message.reply_text(f"{file_type.capitalize()} reçu et distribué à tous les utilisateurs.")

   