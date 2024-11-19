from telegram import Update, Poll
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import asyncio, sqlite3, csv
from sondage.close_poll import close_poll_after_duration
from sondage.send_poll import send_poll_to_all_users
ADMIN_IDS = {1150156856, 7171212138 }  

# États de la conversation
QUESTION, OPTIONS, DURATION = range(3)

# Dictionnaire pour stocker les données de sondage en cours
poll_data = {}

# Commande pour démarrer le processus de création de sondage
async def start_poll_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Seuls les administrateurs peuvent créer des sondages.")
        return ConversationHandler.END
    
    await update.message.reply_text("Entrez la question du sondage :")
    return QUESTION

# Fonction pour récupérer la question
async def receive_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll_data['question'] = update.message.text
    await update.message.reply_text("Entrez les options séparées par des virgules (ex: option1, option2, option3) :")
    return OPTIONS

# Fonction pour récupérer les options
async def receive_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    options = [option.strip() for option in update.message.text.split(",")]
    if len(options) < 2:
        await update.message.reply_text("Veuillez entrer au moins deux options.")
        return OPTIONS
    
    poll_data['options'] = options
    await update.message.reply_text("Entrez la durée du sondage en jours :")
    return DURATION

# Fonction pour récupérer la durée en jours et créer le sondage
async def receive_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        duration_days = int(update.message.text)
        poll_data['duration'] = duration_days
    except ValueError:
        await update.message.reply_text("Veuillez entrer une durée valide en jours. Ex: 2")
        return DURATION

    poll_message = await update.message.reply_poll(
        question=poll_data['question'],
        options=poll_data['options'],
        is_anonymous=False,
        allows_multiple_answers=False
    )
    await update.message.reply_text(f"Sondage créé avec succès pour une durée de {duration_days} jour(s).")
    
    poll_id = poll_message.poll.id
    poll_data['poll_id'] = poll_id 
    
    poll_data['csv_file'] = f"sondage_resultats_{poll_id}.csv"
    with open(poll_data['csv_file'], mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['User ID', 'Selected Option'])
    print("Fichier CSV créé pour le sondage.")
    await send_poll_to_all_users(context,poll_data)

    asyncio.create_task(close_poll_after_duration(context, update.effective_chat.id, poll_message.message_id, duration_days,poll_data,ADMIN_IDS))

    return ConversationHandler.END



# Fonction pour enregistrer les réponses au sondage
async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll_id = update.poll_answer.poll_id
    user_id = update.poll_answer.user.id
    selected_option_index = update.poll_answer.option_ids[0]  
    selected_option = poll_data['options'][selected_option_index]

    with open(poll_data['csv_file'], mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, selected_option])




# Configuration du gestionnaire de conversation pour la création de sondage
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("sondage", start_poll_creation)],
    states={
        QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_question)],
        OPTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_options)],
        DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_duration)],
    },
    fallbacks=[],
)


