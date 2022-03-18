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
from django.http import JsonResponse
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
# third party
from collections import OrderedDict
from rest_framework import viewsets, filters

from .models import *
from .serializers import *
from rest_framework.viewsets import GenericViewSet

class Pagination(PageNumberPagination):
	page_size = 10
	def get_paginated_response(self, data):
		return Response(OrderedDict([
			('next', self.get_next_link()),
			('previous', self.get_previous_link()),
			('count', self.page.paginator.count),
			('page', self.page.number),
			('num_page', self.page.paginator.num_pages),
			('results', data)
		]))


class TokenPairView(TokenObtainPairView):
	serializer_class = TokenPairSerializer

class UserViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated, IsAdminUser]
	queryset = User.objects.filter()
	pagination_class = Pagination
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
	pagination_class = Pagination
	serializer_class = AccountSerializer
	filter_backends = DjangoFilterBackend,
	filter_fields = {
		"date":["exact"]
	}
class TauxViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated, ]
	queryset = Taux.objects.all()
	pagination_class = Pagination
	serializer_class = TauxSerializer
	filter_backends = (filters.SearchFilter,)
	search_fields = ('taux', 'date')


class TransferViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated, ]
	queryset = Transfer.objects.all()
	pagination_class = Pagination
	serializer_class = TransferSerializer
	filter_backends = (filters.SearchFilter,)
	search_fields = ('nom', 'montant', 'tel', 'date')

	@transaction.atomic
	def create(self, request):
		data = request.data
		compte = Account.objects.all().latest('id')
		taux = Taux.objects.all().latest('id')
		nom = data.get('nom')
		tel = (data.get('tel'))
		montant = float(data.get('montant'))
		# montant_fbu = float(data.get('montant_fbu'))
		transfer = Transfer(
			nom=nom,
			tel=tel,
			taux=taux,
			account=compte,
			montant=montant,
			# status=status,
			# montant_fbu=montant_fbu,
		)
		compte.montant_canada+=transfer.montant
		compte.save()
		transfer.save()
		serializer = TransferSerializer(transfer, many=False).data
		return Response(serializer,200)

	@transaction.atomic
	def update(self, request, pk):
		data = request.data
		compte=Account.objects.all().latest('id')
		taux = Taux.objects.all().latest('id')
		nom = data.get('nom')
		tel = data.get('tel')
		status = data.get('status')
		montant = float(data.get('montant'))
		transfer=self.get_object()
		compte.montant_canada -= transfer.montant
		transfer.nom= nom
		transfer.montant= montant
		transfer.tel= tel
		transfer.status= status
		compte.montant_canada+=montant
		compte.save()
		transfer.save()
		serializer = TransferSerializer(transfer, many=False).data
		return Response(serializer,200)

	@transaction.atomic
	def partial_update(self, request, *args, **kwargs):
		data = request.data
		compte=Account.objects.all().latest('id')
		transfer=self.get_object()
		if (request.data['is_valid'] =='servi'):
			transfer.counter+=1
			if transfer.counter==1:
				compte.montant_burundi-=transfer.montant*transfer.taux.taux
			else:
				pass
			compte.save()
		serializer = TransferSerializer(transfer, data=request.data, partial=True) # set partial=True to update a data partially
		if serializer.is_valid():
			serializer.save()
			return JsonResponse(status=201, data=serializer.data)
		return JsonResponse(status=400, data="wrong parameters")

	@transaction.atomic
	def destroy(self,request, pk):
		transfer=self.get_object()
		compte=Account.objects.all().latest('id')
		compte.montant_canada -= transfer.montant
		compte.montant_burundi += transfer.montant*transfer.taux.taux
		compte.save()
		transfer.delete()
		serializer = TransferSerializer(transfer, many=False).data
		return Response(serializer,200)

class ProvisioningViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated, ]
	pagination_class = Pagination
	queryset = Provisioning.objects.all()
	serializer_class = ProvisioningSerializer
	filter_backends = (filters.SearchFilter,)
	search_fields = ('montant_recu', 'date')

	@transaction.atomic
	def create(self, request):
		data = request.data
		account = Account.objects.all().latest('id')
		montant_recu = float(data.get('montant_recu'))
		montant = float(data.get('montant'))
		approvision =Provisioning(
			montant_recu=montant_recu,
			account=account,
			montant=montant
		)
		# account.montant_canada -=montant
		# account.montant_burundi += montant_recu
		account.save()
		approvision.save()
		serializer = ProvisioningSerializer(approvision, many=False).data
		return Response(serializer,200)


	@transaction.atomic
	def update(self, request, pk):
		data = request.data
		compte=Account.objects.all().latest('id')
		montant_recu =float(data.get('montant_recu'))
		montant = float(data.get('montant'))
		approvision=self.get_object()
		# compte.montant_burundi -=approvision.montant_recu
		# compte.montant_canada +=approvision.montant
		approvision.montant = montant
		approvision.montant_recu = montant_recu
		# compte.montant_canada -=montant
		# compte.montant_burundi += montant_recu
		compte.save()
		approvision.save()
		serializer = ProvisioningSerializer(approvision, many=False).data
		return Response(serializer,200)

	@transaction.atomic
	def partial_update(self, request, *args, **kwargs):
		data = request.data
		compte=Account.objects.all().latest('id')
		approvision=self.get_object()
		if (request.data['validate'] =='Validé'):
			approvision.counter+=1
			if approvision.counter==1:
				compte.montant_burundi+=approvision.montant_recu
				compte.montant_canada-=approvision.montant
			compte.save()
		serializer = ProvisioningSerializer(approvision, data=request.data, partial=True) # set partial=True to update a data partially
		if serializer.is_valid():
			serializer.save()
			return JsonResponse(status=201, data=serializer.data)
		return JsonResponse(status=400, data="wrong parameters")

	@transaction.atomic
	def destroy(self,request, pk):
		data=request.data
		approvision=self.get_object()
		compte=Account.objects.all().latest('id')
		if (approvision.validate =='Validé'):
			compte.montant_burundi -= approvision.montant_recu
			compte.montant_canada += approvision.montant
			compte.save()
		approvision.delete()
		serializer = ProvisioningSerializer(approvision, many=False).data
		return Response(serializer,200)


class DepenseViewset(viewsets.ModelViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated, ]
	queryset = Depense.objects.all()
	pagination_class = Pagination
	serializer_class = DepenseSerializer
	filter_backends = (filters.SearchFilter,)
	search_fields = ('montant','date')

	@transaction.atomic
	def create(self, request):
		data = request.data
		account = Account.objects.all().latest('id')
		montant = float(data.get('montant'))
		motif = (data.get('motif'))
		depense = Depense(
			montant=montant,
			account=account,
			motif=motif,
		)
		account.save()
		depense.save()
		serializer = DepenseSerializer(depense, many=False).data
		return Response(serializer,200)

	@transaction.atomic
	def update(self, request, pk):
		data = request.data
		compte=Account.objects.all().latest('id')
		depense=self.get_object()
		validate = (data.get('validate'))
		compte.save()
		depense.save()
		serializer = DepenseSerializer(depense, many=False).data
		return Response(serializer,200)

	@transaction.atomic
	def partial_update(self, request, *args, **kwargs):
		data = request.data
		compte = Account.objects.all().latest('id')
		# montant = float(data.get('montant'))
		depense=self.get_object()
		serializer = DepenseSerializer(depense, data=request.data, partial=True) # set partial=True to update a data partially
		if (request.data['validate'] =='Validé'):
			depense.counter+=1
			if depense.counter==1:
				compte.montant_burundi-=depense.montant
			else:
				pass
			compte.save()
		if serializer.is_valid():
			serializer.save()
			return JsonResponse(status=201, data=serializer.data)
		return JsonResponse(status=400, data="wrong parameters")

	@transaction.atomic
	def destroy(self,request, pk):
		depense=self.get_object()
		compte=Account.objects.all().latest('id')
		compte.save()
		depense.delete()
		serializer = DepenseSerializer(depense, many=False).data
		return Response(serializer,200)



class StatViewset(viewsets.GenericViewSet):
	authentication_classes = (SessionAuthentication, JWTAuthentication)
	permission_classes = [IsAuthenticated, ]
	pagination_class = Pagination
	queryset = Depense.objects.all()
	filter_backends = (filters.SearchFilter,)
	search_fields = ('montant','date')

	def list(self,request):
		depenses = Depense.objects.all()
		approvisions = Provisioning.objects.all()
		transfers = Transfer.objects.all()

		result=[]
		for transfer in transfers:
			if transfer.is_valid=='servi':
				result.append({
					'date':transfer.date,
					'activite': "Transfer",
					'libelle' : 'Chez '+transfer.nom,
					'montant' : transfer.montant*transfer.taux.taux

					})
		for depense in depenses:
			if depense.validate=='Validé':
				result.append({
					'date':depense.date,
					'activite': 'Depense',
					'libelle' : depense.motif,
					'montant' : depense.montant

					})
		for approvision in approvisions:
			if approvision.validate=='Validé':
				result.append({
					'date':approvision.date,
					'activite': "Approvision",
					'libelle' : approvision.montant,
					'montant' : approvision.montant_recu

					})
		serializer=StatSerializer(result, many=True)

		return Response(serializer.data, 200)