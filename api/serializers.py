from rest_framework.exceptions import NotFound
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password


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
		exclude = "last_login","is_staff","email","date_joined","user_permissions"

class ClientSerializer(serializers.ModelSerializer):
	class Meta:
		model = Client
		fields = "__all__"

class LastLoginSerializer(serializers.ModelSerializer):
	class Meta:
		model = LastLogin
		fields = "__all__"
