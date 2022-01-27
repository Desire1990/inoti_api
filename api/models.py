from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group
from datetime import datetime


STATUS=(
	('default', 'default'),
	('appel', 'appel'),
	('servi', 'servi')
)
class LastLogin(models.Model):
	id = models.SmallAutoField(primary_key=True)
	date = models.DateTimeField(default=timezone.now, editable=False)


class Account(models.Model):
	id = models.SmallAutoField(primary_key=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	montant_canada = models.FloatField(default = 0)
	montant_burundi = models.FloatField(default = 0)
	code=models.CharField(max_length=50, null=True,blank=True)
	date  = models.DateTimeField(default = timezone.now, editable = False)

	def __str__(self):
		return f"{self.montant_canada}"



class Transfer(models.Model):
	id = models.SmallAutoField(primary_key=True)
	account=models.ForeignKey(Account, on_delete = models.CASCADE)
	nom = models.CharField(max_length=64, null=True)
	montant = models.FloatField(default=0)
	montant_fbu = models.FloatField(default = 0)
	tel = models.CharField(max_length=20, unique = True)
	date  = models.DateTimeField(default = timezone.now, editable = False)
	taux = models.FloatField(default=3500, null=True)
	status = models.CharField(max_length=20, choices=STATUS)

	def __str__(self):
		return f"{self.nom}"
	
	class Meta: # Order post by date
  		ordering = ['-date',]



class Transaction(models.Model):
	id = models.SmallAutoField(primary_key = True)
	sent = models.ForeignKey(Account, on_delete = models.CASCADE)
	receiver = models.CharField(max_length= 100)
	amount = models.FloatField(default = 0)
	date = models.DateTimeField(default = timezone.now, editable=False)

	def __str__(self):
		return f"{self.amount}"


class Provisioning(models.Model):
	id = models.SmallAutoField(primary_key=True)
	account  = models.ForeignKey(Account, on_delete = models.PROTECT)
	montant = models.FloatField(default=0)
	montant_recu = models.FloatField(default=0)
	date = models.DateTimeField(default=timezone.now, editable = False)
	def __str__(self):
		return f"{self.user.username} {self.montant}"

class Depense(models.Model):
	id = models.SmallAutoField(primary_key=True)
	account  = models.ForeignKey(Account, on_delete = models.PROTECT)
	montant = models.FloatField(default = 0)
	date = models.DateTimeField(default=timezone.now, editable = False)
	is_valid = models.BooleanField(default=False)
	motif = models.TextField()

	def __str__(self):
		return f"{self.user.username} {self.montant}"
