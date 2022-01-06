from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group

from datetime import datetime, timedelta, date
from django.core.validators import MaxValueValidator, MinValueValidator

class LastLogin(models.Model):
	id = models.SmallAutoField(primary_key=True)
	date = models.DateTimeField(default=timezone.now, editable=False)

class Client(models.Model):
	nom = models.CharField(max_length=64, null=True)
	montant = models.FloatField(default=0)
	tel = models.CharField(max_length=20, unique = True)

	class Meta:
		unique_together = ('nom', 'tel')

	def __str__(self):
		return f"{self.nom} {self.tel}"


class AccountCanada(models.Model):
	id = models.SmallAutoField(primary_key=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	montant = models.FloatField(default = 0)
	transfer = models.FloatField(default=0)

	def __str__(self):
		return f"self.user.usename"

class AccountBurundi(models.Model):
	id = models.SmallAutoField(primary_key=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	montant = models.FloatField(default = 0)
	transfer = models.FloatField(default=0)

	def __str__(self):
		return f"{self.user.usename}"

class Payment(models.Model):
	id = models.SmallAutoField(primary_key = True)
	client = models.ForeignKey(Client, on_delete = models.CASCADE)
	montant = models.FloatField(default = 0)
	data = models.DateTimeField(default=timezone.now, editable=False)


class Provisioning(models.Model):
	id = models.SmallAutoField(primary_key=True)
	user = models.OneToOneField(User, on_delete = models.CASCADE)
	account  = models.ForeignKey(AccountBurundi, on_delete = models.PROTECT)
	montant = models.FloatField(default=0)
	montant_recu = models.FloatField(default=0)

	def __str__(self):
		return f"{self.user.username} {self.montant}"


class Depense(models.Model):
	id = models.SmallAutoField(primary_key=True)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	montant = models.FloatField(default = 0)
	date = models.DateTimeField(default=timezone.now, editable = False)
	is_valid = models.BooleanField(default = False)

	def __str__(self):
		return f"{self.user.username} {seelf.montant}"
    