from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group
from datetime import datetime
from django.core.validators import RegexValidator

STATUS=(
	('defaut', 'defaut'),
	('appel', 'appel'),
	('servi', 'servi')
)
VALID=(
	('Validé','Validé'),
	('Rejeté', 'Rejeté'),
	('Attente', 'Attente')
	)


phone_regex = RegexValidator(regex=r'^((\+)257|)?[6-7][1-2, 7-9]\d{6}$', message="Phone number must be entered in the format: '+25777777777'. Up to 12 digits allowed.")

class LastLogin(models.Model):
	id = models.SmallAutoField(primary_key=True)
	date = models.DateTimeField(default=timezone.now, editable=False)

class Account(models.Model):
	id = models.SmallAutoField(primary_key=True)
	montant_canada = models.FloatField(default = 0)
	montant_burundi = models.FloatField(default = 0)
	code=models.CharField(max_length=50, null=True,blank=True, editable=False, default='MAIN')
	date  = models.DateTimeField(default = timezone.now, editable = False)

	def __str__(self):
		return f"{self.montant_canada}"
	class Meta: # Order by date
  		
  		ordering = ['-date',]
class Taux(models.Model):
	id = models.SmallAutoField(primary_key=True)
	taux = models.FloatField(default=3500)
	date  = models.DateTimeField(default = timezone.now, editable = False)

	def __str__(self):
		return f"{self.taux}"
	# class Meta: # Order by date
 #  		ordering = ['-date',]

class Transfer(models.Model):
	id = models.SmallAutoField(primary_key=True)
	account=models.ForeignKey(Account, on_delete = models.CASCADE)
	taux = models.ForeignKey(Taux, on_delete=models.CASCADE)
	nom = models.CharField(max_length=64, null=True)
	montant = models.FloatField(default=0)
	montant_fbu = models.FloatField(default = 0)
	tel =  models.CharField(validators=[phone_regex], max_length=12, blank=True)
	date  = models.DateTimeField(default = timezone.now, editable = False)
	# taux = models.FloatField(default=3500, null=True)
	is_valid = models.CharField(max_length=20,default='defaut', choices=STATUS)
	counter = models.PositiveIntegerField(default=0)

	def __str__(self):
		return f"{self.nom}"

	class Meta: # Order by date
  		ordering = ['-date',]

class Provisioning(models.Model):
	id = models.SmallAutoField(primary_key=True)
	account  = models.ForeignKey(Account, on_delete = models.CASCADE)
	montant = models.FloatField(default=0)
	montant_recu = models.FloatField(default=0)
	date = models.DateTimeField(default=timezone.now, editable = False)
	counter = models.PositiveIntegerField(default=0)
	validate = models.CharField(default='Attente', max_length=20, choices=VALID)
	def __str__(self):
		return f"{self.user.username} {self.montant}"

	class Meta: # Order by date
  		ordering = ['date',]

class Depense(models.Model):
	id = models.SmallAutoField(primary_key=True)
	account  = models.ForeignKey(Account, on_delete = models.CASCADE)
	montant = models.FloatField(default = 0)
	date = models.DateTimeField(default=timezone.now, editable = False)
	validate = models.CharField(default='Attente', max_length=20, choices=VALID)
	motif = models.TextField()
	counter = models.PositiveIntegerField(default=0)

	def __str__(self):
		return f"{self.montant}"
	class Meta: # Order by date
  		ordering = ['-date',]
