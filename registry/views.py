from django.shortcuts import render
from rest_framework import viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Customer, Supplier, PaymentOption, ExpenseCategory, Expense, BusinessProfile, AnonymousProfile
from .serializers import CustomerSerializer, SupplierSerializer, PaymentOptionSerializer, ExpenseCategorySerializer, ExpenseSerializer, BusinessProfileSerializer, AnonymousProfileSerializer
from users.models import UserClient

@swagger_auto_schema(tags=["Registry"])
# Create your views here.
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]  

class PaymentOptionViewSet(viewsets.ModelViewSet):
    queryset = PaymentOption.objects.all()
    serializer_class = PaymentOptionSerializer
    permission_classes = [IsAuthenticated]

class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsAuthenticated]

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()    
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

class BusinessProfile(viewsets.ModelViewSet):
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]


class AnonymousProfileViewSet(viewsets.ModelViewSet):
    queryset = AnonymousProfile.objects.all()
    serializer_class = AnonymousProfileSerializer
    permission_classes = [IsAuthenticated]


class AnonymousIdentifySerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False)
    address = serializers.CharField(required=False, allow_blank=True)
    marketing_opt_in = serializers.BooleanField(required=False)
    marketing_channels = serializers.JSONField(required=False)


class AnonymousIdentifyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Convert an anonymous profile into a customer and link future visits.",
        request_body=AnonymousIdentifySerializer,
        responses={
            200: openapi.Response(description="Identified"),
            400: openapi.Response(description="Validation error"),
            404: openapi.Response(description="Anonymous profile not found"),
        },
        tags=['POS Checkout']
    )
    def post(self, request, anonymous_id):
        user_client: UserClient = request.user
        serializer = AnonymousIdentifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data

        try:
            anon = AnonymousProfile.objects.get(pk=anonymous_id)
        except AnonymousProfile.DoesNotExist:
            return Response({"error": "Anonymous profile not found"}, status=status.HTTP_404_NOT_FOUND)

        name = data.get('name') or 'Walk-in'
        phone = data.get('phone')
        email = data.get('email')
        address = data.get('address') or ''
        marketing_opt_in = data.get('marketing_opt_in') or False
        marketing_channels = data.get('marketing_channels')

        customer = None
        qs = Customer.objects.filter(user_client=user_client)
        if phone:
            customer = qs.filter(phone=phone).first()
        if not customer and email:
            customer = qs.filter(email=email).first()
        if not customer:
            customer = Customer.objects.create(
                user_client=user_client,
                name=name,
                email=email,
                phone=phone,
                address=address,
                marketing_opt_in=marketing_opt_in,
                marketing_channels=marketing_channels,
            )

        return Response({
            "message": "Anonymous profile identified",
            "anonymous_customer_id": str(anon.anonymous_customer_id),
            "customer_id": str(customer.customer_id),
        }, status=status.HTTP_200_OK)
