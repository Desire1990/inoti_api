from django.db import connection, transaction, IntegrityError
from django.shortcuts import render
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count
from rest_framework import viewsets, generics, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.db import transaction
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from django_filters import rest_framework as filters


from .models import *
from .serializers import *

class TokenPairView(TokenObtainPairView):
	serializer_class = TokenPairSerializer

class UserViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated, IsAdminUser]
	queryset = User.objects.filter()
	serializer_class = UserSerializer
	filter_backends = DjangoFilterBackend,
	filter_fields = {

		"username":["exact"]
	}

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = request.data
		user = User(
			username = data.get("username"),
			email = data.get("email"),
			first_name = data.get("first_name"),
			last_name = data.get("last_name")
		)
		user.set_password("password")
		
		user.save()
		serializer = UserSerializer(user, many=False)
		return Response(serializer.data, 201)

	def update(self, request, *args, **kwargs):
		user = request.user
		data = request.data
		username = data.get("username")
		if username : user.username = username
		password = data.get("password")
		if password : user.set_password(password)
		user.save()
		serializer = UserSerializer(user, many=False)
		return Response(serializer.data, 201)

	def patch(self, request, *args, **kwargs):
		return self.update(request, *args, **kwargs)

	def destroy(self, request, *args, **kwargs):
		user = self.get_object()
		user.is_active = False
		user.save()
		return Response({'status': 'success'}, 204)


class AccountViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated, ]
	queryset = Account.objects.all()
	serializer_class = AccountSerializer
	filter_backends = DjangoFilterBackend,
	filter_fields = {
		"date":["exact"]
	}

class TransferViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated, ]
	queryset = Transfer.objects.all()
	serializer_class = TransferSerializer
	filter_backends = DjangoFilterBackend,
	filter_fields = {

		"account":["exact"]
	}
	@transaction.atomic
	def create(self, request):
		data = request.data
		compte = Account.objects.get(code='MAIN')
		nom = data.get('nom')
		tel = data.get('tel')
		montant = float(data.get('montant'))
		transfer = Transfer(
			nom=nom,
			tel=tel,
			account=compte,
			montant=montant
		)
		compte.montant_canada += montant
		compte.save()
		transfer.save()
		return Response({'status':'Depot effecue avec succes'},200)

	@transaction.atomic
	def update(self, request, pk):
		data = request.data
		compte = Account.objects.get(code='MAIN')
		nom = data.get('nom')
		tel = data.get('tel')
		montant_fbu =float(data.get('montant_fbu'))
		taux = float(data.get('taux'))
		montant = float(data.get('montant'))
		transfer=self.get_object()
		compte.montant_canada-=transfer.montant
		transfer.nom= nom
		transfer.montant= montant
		transfer.montant_fbu= montant_fbu
		transfer.taux= taux
		transfer.tel= tel
		compte.montant_canada+=montant
		compte.save()
		transfer.save()
		return Response({'status':'Depot updated avec succes'},200)

	@transaction.atomic
	def destroy(self,request, pk):
		transfer=self.get_object()
		compte = Account.objects.get(code='MAIN')
		compte.montant_canada -= transfer.montant
		compte.save()
		transfer.delete()
		return Response({'status': 'success'}, 204)



class TransactionViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated, ]
	queryset = Transaction.objects.all()
	serializer_class = TransactionSerializer
	filter_backends = DjangoFilterBackend,
	filter_fields = {

		"amount":["exact"]
	}
	@transaction.atomic
	def create(self, request): 
		data = request.data
		account = Account.objects.get(code='MAIN')
		receiver = data.get('receiver')
		amount = float(data.get('amount'))
		transaction = Transaction(
			receiver=receiver,
			sent=account,
			amount=amount
		)
		account.montant_burundi-=amount
		account.save()
		transaction.save()
		return Response({'status':'transaction effecue avec succes'},200)

class DepenseViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated, ]
	queryset = Depense.objects.all()
	serializer_class = DepenseSerializer
	filter_backends = DjangoFilterBackend,
	filter_fields = {

		"date":["exact"]
	}
	@transaction.atomic
	def create(self, request): 
		data = request.data
		account = Account.objects.get(code='MAIN')
		montant = float(data.get('montant'))
		is_valid = (data.get('is_valid'))
		depense =Depense(
			montant=montant,
			is_valid=is_valid
		)
		if depense.is_valid:
			account.montant_burundi -= montant
			account.save()
			depense.save()
		return Response({'status':'depasse validee avec succes'},200)




class ProvisioningViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated, ]
	queryset = Provisioning.objects.all()
	serializer_class = ProvisioningSerializer
	filter_backends = DjangoFilterBackend,
	filter_fields = {

		"montant_recu":["exact"]
	}
	@transaction.atomic
	def create(self, request): 
		data = request.data
		account = Account.objects.get(code='MAIN')
		montant_recu = float(data.get('montant_recu'))
		montant = float(data.get('montant'))
		approvision =Provisioning(
			montant_recu=montant_recu,
			account=account,
			montant=montant
		)
		account.montant_canada -=montant
		account.montant_burundi += montant_recu
		account.save()
		approvision.save()
		serializer = ProvisioningSerializer(approvision, many=False).data
		return Response(serializer,200)


	@transaction.atomic
	def update(self, request, pk):
		data = request.data
		compte = Account.objects.get(code='MAIN')
		montant_recu =float(data.get('montant_recu'))
		montant = float(data.get('montant'))
		approvision=self.get_object()
		compte.montant_burundi -=approvision.montant_recu
		compte.montant_canada +=approvision.montant
		approvision.montant = montant
		approvision.montant_recu = montant_recu
		compte.montant_canada -=montant
		compte.montant_burundi += montant_recu
		compte.save()
		approvision.save()
		serializer = ProvisioningSerializer(approvision, many=False).data
		return Response(serializer,200)


	@transaction.atomic
	def destroy(self,request, pk):
		approvision=self.get_object()
		compte = Account.objects.get(code='MAIN')
		compte.montant_burundi -= approvision.montant_recu 
		compte.montant_canada += approvision.montant
		compte.save()
		approvision.delete()
		return Response({'status': 'success'}, 204)

