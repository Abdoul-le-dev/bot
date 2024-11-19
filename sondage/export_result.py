
from telegram import Update, Poll
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Fonction pour exporter les résultats au format CSV et envoyer à l'admin
async def export_results_to_admin(context: ContextTypes.DEFAULT_TYPE, poll_data,ADMIN_IDS):
    csv_file = poll_data.get('csv_file')
    if not csv_file:
        print("Erreur : Fichier CSV introuvable.")
        return

    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_document(chat_id=admin_id, document=open(csv_file, 'rb'))
        except Exception as e:
            print(f"Erreur lors de l'envoi du fichier CSV à l'administrateur {admin_id} : {e}")