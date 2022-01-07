from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.db.models import Sum
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


class Account(models.Model):
	id = models.SmallAutoField(primary_key=True)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	montant_canada = models.FloatField(default = 0)
	montant_burundi = models.FloatField(default = 0)
	date  = models.DateTimeField(default = timezone.now, editable = False)
	def __str__(self):
		return f"{self.montant_canada}"

	# class Meta:
	# 	constraints = [
	# 		models.CheckConstraint(check=models.Q(montant_canada__gte='0'), name='d_montant_canada_cannot_be_negative'),
	# 	]

	# class Meta:
	# 	constraints = [
	# 		models.CheckConstraint(check=models.Q(montant_burundi__gte='0'), name='d_montant_burundi_cannot_be_negative'),
	# 	]


	def get_total_canada(self):
		return self.montant_canada.aggregate(Sum('montant_canada'))['canada__sum']

	def get_total_burundi(self):
		return self.montant_burundi.aggregate(Sum('montant_burundi'))['burundi__sum']



class Depot(models.Model):
	id = models.SmallAutoField(primary_key=True)
	# sender = models.ForeignKey(Client, on_delete = models.CASCADE)
	nom = models.CharField(max_length=64, null=True)
	receiver=models.ForeignKey(Account, on_delete = models.CASCADE)
	amount = models.FloatField(default = 0)
	gain = models.FloatField(default = 0, editable=False)
	date  = models.DateTimeField(default = timezone.now, editable = False)
	taux = models.FloatField(default=0.05, editable=False)

	def __str__(self):
		return f"{self.nom}"

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		receive = self.receiver
		receive.montant_canada += (self.amount)
		self.gain += self.amount*self.taux
		receive.save()

	# class Meta:
	# 	constraints = [
	# 		models.CheckConstraint(check=models.Q(amount__gte='0'), name='d_amount_cannot_be_negative'),
	# 	]


class Transaction(models.Model):
	id = models.SmallAutoField(primary_key = True)
	sent = models.ForeignKey(Account, on_delete = models.CASCADE)
	receiver = models.CharField(max_length= 100)
	amount = models.FloatField(default = 0)
	date = models.DateTimeField(default = timezone.now, editable=False)

	def __str__(self):
		return f"{self.amount}"

	# class Meta:
	# 	constraints = [
	# 		models.CheckConstraint(check=models.Q(amount__gte='0'), name='d_amount_cannot_be_negative'),
	# 	]

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		money = self.sent
		money.montant_burundi -= self.amount
		money.save()



class Depense(models.Model):
	id = models.SmallAutoField(primary_key=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	account = models.ForeignKey(Account, on_delete=models.CASCADE)
	montant = models.FloatField(default = 0)
	date = models.DateTimeField(default=timezone.now, editable = False)
	is_valid = models.BooleanField(default = False)

	def __str__(self):
		return f"{self.user.username} {self.montant}"

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		payee = self.account
		payee.montant -= self.montant
		payee.save()

	
	# class Meta:
	# 	constraints = [
	# 		models.CheckConstraint(check=models.Q(montant__gte='0'), name='d_montant_cannot_be_negative'),
	# 	]


class Payment(models.Model):
	id = models.SmallAutoField(primary_key = True)
	user = models.OneToOneField(User, on_delete = models.CASCADE)
	account = models.ForeignKey(Account, on_delete = models.CASCADE)
	montant = models.FloatField(default = 0)
	date = models.DateTimeField(default=timezone.now, editable=False)

	def __str__(self):
		return f"{self.user.username} {self.client.nom} {self.mont}"

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		payee = self.account
		payee.montant_burundi -= self.montant
		payee.save()

	# class Meta:
	# 	constraints = [
	# 		models.CheckConstraint(check=models.Q(amount__gte='0'), name='d_amount_cannot_be_negative'),
	# 	]


class Provisioning(models.Model):
	id = models.SmallAutoField(primary_key=True)
	account  = models.ForeignKey(Account, on_delete = models.PROTECT)
	montant = models.FloatField(default=0)
	montant_recu = models.FloatField(default=0)

	def __str__(self):
		return f"{self.user.username} {self.montant}"

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		provision = self.account
		provision.montant_canada -= self.montant
		provision.montant_burundi += self.montant_recu
		provision.save()

	# class Meta:
	# 	constraints = [
	# 		models.CheckConstraint(check=models.Q(montant__gte='0'), name='d_montant_cannot_be_negative'),
	# 	]