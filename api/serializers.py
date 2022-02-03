from rest_framework.exceptions import NotFound
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.db.models import Sum


class RegisterSerializer(serializers.ModelSerializer):
	email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
	password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

	class Meta:
		model = User
		fields = ('username','first_name', 'last_name', 'email', 'password')
		extra_kwargs = {
			'first_name': {'required': True},
			'last_name': {'required': True}
		}

	def create(self, validated_data):
		user = User.objects.create(
			first_name=validated_data['first_name'],
			last_name=validated_data['last_name'],
			email=validated_data['email'],
		)

		user.set_password(validated_data['password'])
		user.save()

		return user


class TokenPairSerializer(TokenObtainPairSerializer):

	def getGroups(self, user):
		groups = []
		if user.is_superuser:
			groups.append("admin")
		for group in user.groups.all():
			groups.append(group.name)
		return groups

	def validate(self, attrs):
		data = super(TokenPairSerializer, self).validate(attrs)
		data['services'] = [group.name for group in self.user.groups.all()]
		data['is_admin'] = self.user.is_superuser
		data['groups'] = self.getGroups(self.user)
		data['username'] = self.user.username
		data['first_name'] = self.user.first_name
		data['last_name'] = self.user.last_name
		data['email'] = self.user.email
		data['id'] = self.user.id
		logins = LastLogin.objects.all()
		if(logins):
			last_login = logins.first()
			last_login.date = timezone.now()
			last_login.save()
		else:
			LastLogin().save()
		return data

class UserSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True)
	groups = serializers.SerializerMethodField()

	def get_groups(self, user):
		groups = []
		if user.is_superuser:
			groups.append("admin")
		for group in user.groups.all():
			groups.append(group.name)
		return groups

	class Meta:
		model = User
		exclude = "last_login","is_staff","date_joined","user_permissions"
		depth=1

class LastLoginSerializer(serializers.ModelSerializer):
	class Meta:
		model = LastLogin
		fields = "__all__"


class AccountSerializer(serializers.ModelSerializer):
	total_canada = serializers.SerializerMethodField()
	total_burundi = serializers.SerializerMethodField()

	def get_total_canada(self, obj):
		totaux= Account.objects.all().aggregate(total=Sum('montant_canada'))
		return totaux["total"]

	def get_total_burundi(self, obj):
		totaux = Account.objects.all().aggregate(totale=Sum('montant_burundi'))
		return totaux["totale"]

	 
	class Meta:
		model = Account
		fields = "__all__"
		depth=1

class TransferSerializer(serializers.ModelSerializer):
	montant_fbu = serializers.SerializerMethodField()

	def get_montant_fbu(self, instance):
		return float(instance.montant)*float(instance.taux.taux)

	class Meta:
		model = Transfer
		fields = ("__all__")
		depth=1


class DepenseSerializer(serializers.ModelSerializer):
	user = serializers.HiddenField(default=serializers.CurrentUserDefault())
	class Meta:
		model = Depense
		fields = "__all__"
		depth=1

class ProvisioningSerializer(serializers.ModelSerializer):
	class Meta:
		model = Provisioning
		fields = "__all__"
		depth=1

class TauxSerializer(serializers.ModelSerializer):
	class Meta:
		model = Taux
		fields = "__all__"
		depth=1
