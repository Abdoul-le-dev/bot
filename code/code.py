import sys
import os
import re
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')
import django
from django.db import models
from asgiref.sync import sync_to_async
django.setup()
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bots.models import Utilisateur


load_dotenv()

token = os.getenv('TOKEN')

# Dictionnaire pour stocker les informations utilisateur temporairement
user_data = {}

country_code_mapping = {
    "Bénin (+229)": "+229",
    "Burkina Faso (+226)": "+226",
    "Cameroun (+237)": "+237",
    "Côte d'Ivoire (+225)": "+225",
    "Mali (+223)": "+223",
    "Niger (+227)": "+227",
    "Rwanda (+250)": "+250",
    "Sénégal (+221)": "+221",
    "Togo (+228)": "+228",
    "Tunisie (+216)": "+216",
    "Ghana (+233)": "+233",
    "Kenya (+254)": "+254",
    "Nigeria (+234)": "+234",
    "South Africa (+27)": "+27",
    "Uganda (+256)": "+256",
    "Zambia (+260)": "+260",
    "Zimbabwe (+263)": "+263",
    "France (+33)": "+33",
    "Germany (+49)": "+49",
    "Italy (+39)": "+39",
    "Spain (+34)": "+34",
    "Netherlands (+31)": "+31",
    "Belgium (+32)": "+32",
    "Portugal (+351)": "+351",
    "Greece (+30)": "+30",
    "Austria (+43)": "+43",
    "Poland (+48)": "+48",
    "Sweden (+46)": "+46",
    "Denmark (+45)": "+45",
    "Finland (+358)": "+358",
    "Ireland (+353)": "+353",
    "Czech Republic (+420)": "+420",
    "Hungary (+36)": "+36",
    "Slovakia (+421)": "+421",
    "Slovenia (+386)": "+386",
    "Lithuania (+370)": "+370",
    "Latvia (+371)": "+371",
    "Estonia (+372)": "+372",
    "Luxembourg (+352)": "+352",
    "Bulgaria (+359)": "+359",
    "Romania (+40)": "+40",
    "Croatia (+385)": "+385",
    "United States (+1)": "+1",
    "United Kingdom (+44)": "+44",
    "India (+91)": "+91",
    "Canada (+1)": "+1",
    "Australia (+61)": "+61",
}

# Dictionnaire pour la longueur des numéros de téléphone par indicatif de pays
phone_number_length = {
    "+229": 8,    # Bénin
    "+226": 8,    # Burkina Faso
    "+237": 9,    # Cameroun
    "+225": 10,   # Côte d'Ivoire
    "+223": 8,    # Mali
    "+227": 8,    # Niger
    "+250": 10,   # Rwanda
    "+221": 9,    # Sénégal
    "+228": 8,    # Togo
    "+216": 8,    # Tunisie
    "+33": 9,     # France (sans le premier 0)
    "+49": 10,    # Allemagne
    "+39": 10,    # Italie
    "+34": 9,     # Espagne
    "+44": 10,    # Royaume-Uni
    "+41": 9,     # Suisse
    "+32": 9,     # Belgique
    "+351": 9,    # Portugal
    "+43": 10,    # Autriche
    "+358": 9,    # Finlande
    "+45": 8,     # Danemark
    "+46": 9,     # Suède
    "+47": 8,     # Norvège
    "+31": 9,     # Pays-Bas
    "+1": 10,     # USA, Canada
    "+7": 10,     # Russie
    "+91": 10,    # Inde
    "+81": 10,    # Japon
    "+61": 9,     # Australie
    "+55": 11,    # Brésil
    "+52": 10,    # Mexique
    "+86": 11,    # Chine
    "+27": 9,     # Afrique du Sud
    "+234": 10,   # Nigeria
    "+254": 9,    # Kenya
    "+233": 9,    # Ghana
    "+212": 9,    # Maroc
    "+20": 10,    # Égypte
    "+971": 9,    # Émirats arabes unis
    "+966": 9,    # Arabie saoudite
    "+62": 10,    # Indonésie
    "+63": 10,    # Philippines
    "+48": 9,     # Pologne
    "+351": 9,    # Portugal
    "+420": 9,    # République tchèque
    "+90": 10,    # Turquie
    "+82": 10,    # Corée du Sud
    "+94": 9,     # Sri Lanka
    "+66": 9,     # Thaïlande
    "+977": 10,   # Népal
    "+880": 10,   # Bangladesh
}



@sync_to_async
def enregistrer_utilisateur(telegram_user_id, indicatif, numero, nom, prenom, consentement):
    user, created = Utilisateur.objects.get_or_create(
        telegram_user_id=telegram_user_id,
        defaults={
            'indicatif': indicatif,
            'numero': numero,
            'nom': nom,
            'prenom': prenom,
            'consentement': consentement
        }
    )
    if not created:
        user.indicatif = indicatif
        user.numero = numero
        user.nom = nom
        user.prenom = prenom
        user.consentement = consentement
        user.save()
    return user


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id  # ID de l'utilisateur
    user_data[user_id] = {"id": user_id}

    keyboard = [
        [KeyboardButton("J'accepte"), KeyboardButton("Je décline")]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await update.message.reply_text("""Bonjour, je suis Thomas.

Avant de commencer, nous souhaiterions établir un premier contact afin de mieux vous accompagner. En enregistrant votre contact, vous aurez un accès facile à toutes nos actualités et ressources.

Merci de bien vouloir confirmer votre consentement pour l’enregistrement de ces informations.

Soyez assuré que nous respectons pleinement votre vie privée, vous pouvez demander la suppression de vos informations à tout moment.""", reply_markup=reply_markup)
    
    user_data[user_id]["step"] = "awaiting_consent"


async def responce_consentement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_response = update.message.text

    if user_id in user_data:
        etape_actuel = user_data[user_id].get('step')

        if etape_actuel == "awaiting_consent":
            if user_response == "J'accepte":
                user_data[user_id]["consentement"] = "J'accepte"
                keyboard = [
                    # Francophone countries worldwide
                    [KeyboardButton("Bénin (+229)"), KeyboardButton("Burkina Faso (+226)")],
                    [KeyboardButton("Cameroun (+237)"), KeyboardButton("Côte d'Ivoire (+225)")],
                    [KeyboardButton("Mali (+223)"), KeyboardButton("Niger (+227)")],
                    [KeyboardButton("Rwanda (+250)"), KeyboardButton("Sénégal (+221)")],
                    [KeyboardButton("Togo (+228)"), KeyboardButton("Tunisie (+216)")],

                    # Anglophone countries in Africa
                    [KeyboardButton("Ghana (+233)"), KeyboardButton("Kenya (+254)")],
                    [KeyboardButton("Nigeria (+234)"), KeyboardButton("South Africa (+27)")],
                    [KeyboardButton("Uganda (+256)"), KeyboardButton("Zambia (+260)")],
                    [KeyboardButton("Zimbabwe (+263)")],

                     # European Union countries
                    [KeyboardButton("France (+33)"), KeyboardButton("Germany (+49)")],
                    [KeyboardButton("Italy (+39)"), KeyboardButton("Spain (+34)")],
                    [KeyboardButton("Netherlands (+31)"), KeyboardButton("Belgium (+32)")],
                    [KeyboardButton("Portugal (+351)"), KeyboardButton("Greece (+30)")],
                    [KeyboardButton("Austria (+43)"), KeyboardButton("Poland (+48)")],
                    [KeyboardButton("Sweden (+46)"), KeyboardButton("Denmark (+45)")],
                    [KeyboardButton("Finland (+358)"), KeyboardButton("Ireland (+353)")],
                    [KeyboardButton("Czech Republic (+420)"), KeyboardButton("Hungary (+36)")],
                    [KeyboardButton("Slovakia (+421)"), KeyboardButton("Slovenia (+386)")],
                    [KeyboardButton("Lithuania (+370)"), KeyboardButton("Latvia (+371)")],
                    [KeyboardButton("Estonia (+372)"), KeyboardButton("Luxembourg (+352)")],
                    [KeyboardButton("Bulgaria (+359)"), KeyboardButton("Romania (+40)")],
                    [KeyboardButton("Croatia (+385)")],

                    # Other countries
                    [KeyboardButton("United States (+1)"), KeyboardButton("United Kingdom (+44)")],
                    [KeyboardButton("India (+91)"), KeyboardButton("Canada (+1)")],
                    [KeyboardButton("Australia (+61)")],
                ]

                # Creating the markup for the keyboard
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

                await update.message.reply_text("""Merci pour votre consentement ! Veuillez sélectionner l'indicatif du numéro avec lequel vous nous écrivez(ex : +229 66283896 pour le Bénin) :""",reply_markup=reply_markup)
                user_data[user_id]["step"] = "country_code"
            elif user_response == "Je décline":
                await update.message.reply_text("Nous respectons votre décision. N'hésitez pas à revenir vers nous si vous changez d'avis.")
                del user_data[user_id]  # Supprimer les informations de l'utilisateur s'il décline

        elif etape_actuel == "country_code":
            if user_response in country_code_mapping:
                user_data[user_id]["country_code"] = country_code_mapping[user_response]
                print(f"Country code set to {user_data[user_id]['country_code']} for user {user_id}")
            else:
                print("Section invalide. Veuillez selectionnez les pays sur la liste.")
                user_data[user_id]["country_code"] = user_response

            keyboard = [[KeyboardButton("Partager mon numéro", request_contact=True)]]

            # Configurer le clavier pour n'afficher que ce bouton
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
            await update.message.reply_text("Merci ! Veuillez maintenant entrer votre numéro de téléphone (sans l'indicatif) :" ,reply_markup=reply_markup)
            user_data[user_id]["step"] = "awaiting_phone"

        elif etape_actuel == "awaiting_phone":
            user_data[user_id]["phone"] = user_response
            await update.message.reply_text("Merci ! Veuillez maintenant entrer votre nom :")
            user_data[user_id]["step"] = "awaiting_last_name"

        elif etape_actuel == "awaiting_last_name":
            user_data[user_id]["last_name"] = user_response
            await update.message.reply_text("Merci ! Enfin, veuillez entrer votre prénom :")
            user_data[user_id]["step"] = "awaiting_first_name"

        elif etape_actuel == "awaiting_first_name":
            user_data[user_id]["first_name"] = user_response

            keyboard = [
                [KeyboardButton("Infos correctes"), KeyboardButton("Infos incorrectes")]
            ]

            reply_markup = ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True,
                one_time_keyboard=True
            )

            await update.message.reply_text(f"""Bienvenue dans notre communauté de trading, {user_data[user_id]["first_name"]} !

Nous avons bien enregistré vos informations :
- Indicatif : {user_data[user_id]["country_code"]} 
- Numéro : {user_data[user_id]["phone"]}
- Nom : {user_data[user_id]["last_name"]}
- Prénom : {user_data[user_id]["first_name"]}

Veuillez m'enregistrer si c'est pas fait.

Mon numéro : +229 54545454
Mon nom : Abdoul Abdoul

Nous nous sommes enregistrés à présent, vous aurez ainsi accès à toute ma fil d'actualité, les informations et ressources liées à ma communauté.""", reply_markup=reply_markup)
            
            user_data[user_id]["step"] = "check_info"

        elif etape_actuel == "check_info":
            if user_response == "Infos correctes":
                user = await enregistrer_utilisateur(
                    telegram_user_id=user_id,
                    indicatif=user_data[user_id]['country_code'],
                    numero=user_data[user_id]["phone"],
                    nom=user_data[user_id]["last_name"],
                    prenom=user_data[user_id]["first_name"],
                    consentement=True
                )
                await update.message.reply_text("Vos informations ont été enregistrées avec succès !")

                keyboard = [
                    [KeyboardButton("Initiation au Trading"), KeyboardButton("Rejoindre la formation complète")],
                    [KeyboardButton("Communauté VIP RMI class"), KeyboardButton("Participer aux sessions live")],
                    [KeyboardButton("Mes réseaux sociaux"), KeyboardButton("Prise de rendez-vous")],
                    [KeyboardButton("Questions"), KeyboardButton("Discuter avec moi")]
                ]

                reply_markup = ReplyKeyboardMarkup(
                    keyboard=keyboard,
                    resize_keyboard=True,
                    one_time_keyboard=True
                )

                await update.message.reply_text(
                    "Merci pour la confirmation ! Choisissez une option pour commencer :",
                    reply_markup=reply_markup
                )
                user_data[user_id]["step"] = "menu_options"

            elif user_response == "Infos incorrectes":
                await update.message.reply_text("Reprenons l'enregistrement de vos informations.")
                user_data[user_id]["step"] = "awaiting_country_code"
                await update.message.reply_text("Veuillez entrer l'indicatif de votre pays (ex : +229 pour le Bénin) :")

if __name__ == '__main__':
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler('start', start))
    response_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, responce_consentement)
    app.add_handler(response_handler)

    app.run_polling(poll_interval=2)
