import sys
import os
import re
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
import django
from django.db import models
from asgiref.sync import sync_to_async
django.setup()
# from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, PollAnswerHandler
from django.db.models import Count
from bots.models import Utilisateur
from telegram import InputFile

from broadcasting.share_file import share_file
from broadcasting.share_file import start_distribution
from sondage.create import *
from notification.notify import notify_conv_handler
from reminder.create import reminder_conv_handler


# load_dotenv()

token = "7795455738:AAHb0OwZSbE0x-A8hmX6Lli0v1TnW5UzxY0"

# Dictionnaire pour stocker les informations utilisateur temporairement
user_data = {}
ADMIN_USER_ID = 7171212138 

# Fonction pour créer une entrée vCard
def create_vcard_entry(nom, prenom, numero):
    return f"""
BEGIN:VCARD
VERSION:2.1
N:;{prenom} {nom};;;
FN:{prenom} {nom}
TEL;CELL;PREF:{'+'+ numero}
END:VCARD
""".strip()

# Fonction pour obtenir le nom de fichier du lot actuel
def get_batch_filename(batch_num):
    return f"contacts_{batch_num}.vcf"

@sync_to_async
def save_contact_to_file():
    total_users = Utilisateur.objects.count()
    batch_num = (1 // 1) + (1 if total_users % 100 != 0 else 0)
    filename = get_batch_filename(batch_num)

     # Crée le fichier s'il n'existe pas
    
    if not os.path.exists(filename):
        with open(filename, "w") as file:
            file.write("")

    # Récupère les données du dernier utilisateur enregistré
    last_user = Utilisateur.objects.last()
    contact_entry = create_vcard_entry(last_user.nom, last_user.prenom, last_user.numero)

    # Ajoute le contact au fichier
    with open(filename, "a") as file:
        file.write(contact_entry + "\n")

    return total_users, filename

    

# Fonction pour envoyer le fichier si 100 contacts ont été atteints
async def handle_contact_batch_sending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_users, filename = await save_contact_to_file()

    # Si le nombre total d'utilisateurs est un multiple de 100, envoyer le fichier et préparer un nouveau
    if 1 % 1 == 0:
        await context.bot.send_document(chat_id=ADMIN_USER_ID, document=open(filename, "rb"))
        await update.message.reply_text("Le fichier de contacts a été envoyé à l'administrateur !")

# fonction déclencheuse
async def new_user_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_contact_batch_sending(update, context)
    await update.message.reply_text("Contact enregistré avec succès !")

@sync_to_async
def enregistrer_utilisateur(telegram_user_id, indicatif, numero, nom, prenom, consentement):
    user, created = Utilisateur.objects.get_or_create(
        telegram_user_id=telegram_user_id,
        defaults={
            'numero': numero,
            'nom': nom,
            'prenom': prenom,
            'consentement': consentement
        }
    )
    if not created:
       
        user.numero = numero
        user.nom = nom
        user.prenom = prenom
        user.consentement = consentement
        user.save()

    user_data[telegram_user_id]['id'] = telegram_user_id
    user_data[telegram_user_id]['nom'] = nom
    user_data[telegram_user_id]['prenom'] = prenom
    user_data[telegram_user_id]['numero'] = numero    

    return user


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id  # ID de l'utilisateur
    user_data[user_id] = {"id": user_id}

    keyboard = [
        [KeyboardButton("Je partage mon contact", request_contact=True)],
        [KeyboardButton("Je décline")]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await update.message.reply_text("""
Avant de commencer, nous souhaiterions établir un premier contact afin de mieux vous accompagner. En enregistrant votre contact, vous aurez un accès facile à toutes nos actualités et ressources.

Merci de bien vouloir confirmer votre consentement pour partager votre contact.

Soyez assuré que nous respectons pleinement votre vie privée, vous pouvez demander la suppression de vos informations à tout moment.""", reply_markup=reply_markup)
    
    user_data[user_id]["step"] = "awaiting_consent"


async def responce_consentement(update, context):
    user_id = update.effective_user.id
    user_response = update.message.text

    
    if update.message.contact:
        
        numero = update.message.contact.phone_number
        print(numero)
        first_name = update.message.contact.first_name
        last_name = update.message.contact.last_name
        print(numero,first_name,last_name) 

        await enregistrer_utilisateur(user_id,'+229',numero,first_name, last_name,True)

        
        keyboard = [
            [KeyboardButton("🚀 Je suis débutant: Initiation au Trading")],
            [KeyboardButton("📚 Rejoindre la formation complète")],
            [KeyboardButton("🧭 Avant de vous lancer dans le trading")],
            [KeyboardButton("🌟 Rejoindre la Communauté VIP RMI class")],
            [KeyboardButton("📅 Participer aux sessions live")],
            [KeyboardButton("📖 Recevoir mon livre")],
            [KeyboardButton("🎯 Le guide de performance")],
            [KeyboardButton("🔗 Lien vers tous mes réseaux sociaux")],
            [KeyboardButton("📆 Prise de rendez-vous")],
            [KeyboardButton("❓ Questions (réponse urgente)")],
            [KeyboardButton("💬 Questions")],
            [KeyboardButton("🗣 Discuter avec moi")],
            [KeyboardButton("📲 Recevoir toutes les informations de la communauté")]
        ]


        reply_markup = ReplyKeyboardMarkup(
                    keyboard=keyboard,
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
        
        await update.message.reply_text(
    f"Vos informations ont été enregistrées avec succès, {user_data[user_id]['nom']}! 🎉\n\n"
    "Bienvenue dans la famille ! Ici, nous parlons, vivons, et respirons le trading. "
    "Un menu est à votre disposition pour répondre à toutes vos questions et préoccupations. 🚀", reply_markup=reply_markup
)

async def selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_response = update.message.text
    user_id = update.effective_user.id

  
    with open('../data/1.mp4', 'rb') as video_file:
            await context.bot.send_video(
                chat_id=user_id,
                video=InputFile(video_file),
                caption="Bienvenue dans notre initiation au trading ! 🎥 Voici une vidéo pour bien commencer."
            )


     
     

        





if __name__ == '__main__':
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler('start', start))
    
    response_handler = MessageHandler((filters.TEXT | filters.CONTACT) & ~filters.COMMAND, responce_consentement)
    app.add_handler(response_handler)
    app.add_handler(CommandHandler('yes', selection))
    app.add_handler(CommandHandler('contact',new_user_contact))
    
    # Sondage
    app.add_handler(conv_handler) #commande /sondage
    app.add_handler(PollAnswerHandler(handle_poll_answer))
    
    # envoi de fichiers
    app.add_handler(CommandHandler("fichiers", start_distribution))
    app.add_handler(MessageHandler(filters.ALL, share_file))
    
    # Notification 
    app.add_handler(notify_conv_handler) #commande /notifier
    
    # Rappel
    app.add_handler(reminder_conv_handler) #commande /rappel
    
    
    
   

    print('running...')
    app.run_polling(poll_interval=1)
