from django.db import models

# Create your models here.

class Utilisateur(models.Model):
    telegram_user_id = models.BigIntegerField(unique=True)
    numero = models.CharField(max_length=20)
    nom = models.CharField(max_length=50,blank=True, null=True)
    prenom = models.CharField(max_length=50,blank=True, null=True)
    consentement = models.BooleanField(default=False)
    step = models.CharField(max_length=50)
    date_enregistrement = models.DateTimeField(auto_now_add=True)