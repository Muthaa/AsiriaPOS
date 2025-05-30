from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
from rest_framework import viewsets
from .models import Product, Category, Unit
from .serializers import ProductSerializer, CategorySerializer, UnitSerializer
from authentication.permissions import IsOwner, IsManager, IsEmployee
from rest_framework.permissions import IsAuthenticated

@swagger_auto_schema(tags=["Products"])
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsManager]  

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer  # Assuming you have a serializer for Category as well
    permission_classes = [IsAuthenticated, IsManager]  # Allow only managers to manage categories

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer  # Assuming you have a serializer for Unit as well
    permission_classes = [IsAuthenticated, IsManager]  # Allow only managers to manage units
