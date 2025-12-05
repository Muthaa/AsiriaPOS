from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated  # Change if you want to restrict access
from django.utils.timezone import now
from django.db.models import Sum
from django.db import transaction
from sales.models import SalesHeader, Receipt, SalesDetail
from registry.models import Customer, PaymentOption, AnonymousProfile
from products.models import Product, Unit
from users.models import UserClient
from sales.utils.token_hash import hash_token
import uuid
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import CheckoutInitializeSerializer, ReceiptLinkSerializer
from django.utils.crypto import get_random_string

class TodaysSalesTotalAPIView(APIView):
    permission_classes = [IsAuthenticated]  # ⚠️ For testing; use IsAuthenticated in production

    def get(self, request):
        today = now().date()
        total_sales = SalesHeader.objects.filter(created_at__date=today).aggregate(
            total=Sum("total_price")
        )["total"] or 0

        return Response({"total_sales": float(total_sales)})


class CheckoutInitializeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Initialize checkout: create SalesHeader, line items, and a Receipt. Supports anonymous capture and phone-lite linking.",
        request_body=CheckoutInitializeSerializer,
        responses={
            201: openapi.Response(description="Checkout initialized"),
            400: openapi.Response(description="Validation error"),
        },
        tags=['POS Checkout']
    )
    @transaction.atomic
    def post(self, request):
        user_client: UserClient = request.user
        serializer = CheckoutInitializeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        items = data['items']
        payment_method = data['payment_method']
        payment_option_id = data.get('payment_option_id')
        phone = data.get('phone')
        email = data.get('email')
        mpesa_token = data.get('mpesa_token')
        card_token = data.get('card_token')
        credit_account_code = data.get('credit_account_code')
        terminal_id = data.get('terminal_id')

        try:
            payment_option = PaymentOption.objects.get(pk=payment_option_id) if payment_option_id else None
        except PaymentOption.DoesNotExist:
            return Response({"error": "Invalid payment_option_id"}, status=status.HTTP_400_BAD_REQUEST)

        # Find-or-create customer by phone/email if provided (phone-lite)
        customer = None
        if phone or email:
            customer_qs = Customer.objects.filter(user_client=user_client)
            if phone:
                customer = customer_qs.filter(phone=phone).first()
            if not customer and email:
                customer = customer_qs.filter(email=email).first()
            if not customer:
                customer = Customer.objects.create(
                    user_client=user_client,
                    name=phone or email or "Walk-in",
                    email=email,
                    phone=phone,
                    address="",
                )

        # Calculate totals
        subtotal = 0
        for item in items:
            product_id = item.get('product_id')
            unit_id = item.get('unit_id')
            qty = int(item.get('qty', 0))
            price = float(item.get('price', 0))
            if not product_id or qty <= 0:
                return Response({"error": "Each item needs product_id and qty > 0"}, status=status.HTTP_400_BAD_REQUEST)
            subtotal += qty * price

        total_price = subtotal  # extend later with taxes/discounts
        remaining_balance = 0

        # Create SalesHeader (anonymous if no customer)
        order_number = f"SO-{uuid.uuid4().hex[:8].upper()}"
        sales_header = SalesHeader.objects.create(
            user_client=user_client,
            customer=customer,
            payment_option=payment_option if payment_option else PaymentOption.objects.filter(user_client=user_client).first(),
            order_number=order_number,
            subtotal=subtotal,
            total_price=total_price,
            remaining_balance=remaining_balance,
            payment_method=payment_method,
            terminal_id=terminal_id,
        )

        if not customer:
            # create anonymous profile and attach id
            anon = AnonymousProfile.objects.create(user_client=user_client)
            sales_header.anonymous_customer_id = anon.anonymous_customer_id
            sales_header.save(update_fields=['anonymous_customer_id'])

        # Set hashed tokens if provided
        if mpesa_token:
            sales_header.mpesa_token_hash = hash_token(mpesa_token)
        if card_token:
            sales_header.card_token_hash = hash_token(card_token)
        if credit_account_code:
            sales_header.credit_account_code = credit_account_code
        sales_header.save()

        # Create line items and decrease stock via existing signals
        for item in items:
            product = Product.objects.get(pk=item['product_id'])
            unit = Unit.objects.get(pk=item.get('unit_id', product.unit_id))
            qty = int(item['qty'])
            price = float(item.get('price') or product.price)
            SalesDetail.objects.create(
                sales_header=sales_header,
                user_client=user_client,
                product=product,
                unit=unit,
                quantity=qty,
                price_per_unit=price,
            )

        # Create receipt skeleton (amounts can be adjusted by payment flow)
        receipt_number = f"RC-{uuid.uuid4().hex[:8].upper()}"
        receipt = Receipt.objects.create(
            user_client=user_client,
            customer=customer,
            payment_option=sales_header.payment_option,
            sales_header=sales_header,
            receipt_number=receipt_number,
            total_amount=total_price,
            amount_paid=0,
            narration="",
            payment_method=payment_method,
            anonymous_customer_id=sales_header.anonymous_customer_id,
            mpesa_token_hash=sales_header.mpesa_token_hash,
            card_token_hash=sales_header.card_token_hash,
            credit_account_code=sales_header.credit_account_code,
        )
        # Generate and persist short link token for QR/text
        short_token = get_random_string(10).upper()
        receipt.link_token = short_token
        receipt.save(update_fields=['link_token'])

        return Response({
            "order_number": sales_header.order_number,
            "receipt_number": receipt.receipt_number,
            "receipt_id": str(receipt.receipt_id),
            "short_token": short_token,
            "anonymous_customer_id": str(sales_header.anonymous_customer_id) if sales_header.anonymous_customer_id else None,
            "customer_id": str(customer.customer_id) if customer else None,
            "total_price": float(total_price),
        }, status=status.HTTP_201_CREATED)


class ReceiptLinkTokenSerializer(ReceiptLinkSerializer):
    token = serializers.CharField()


class ReceiptLinkAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Link an existing anonymous receipt to a customer using phone/email.",
        request_body=ReceiptLinkSerializer,
        responses={
            200: openapi.Response(description="Linked"),
            400: openapi.Response(description="Validation error"),
            404: openapi.Response(description="Not found"),
        },
        tags=['POS Checkout']
    )
    @transaction.atomic
    def post(self, request):
        user_client: UserClient = request.user
        serializer = ReceiptLinkSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        receipt_id = data['receipt_id']
        phone = data.get('phone')
        email = data.get('email')
        try:
            receipt = Receipt.objects.get(pk=receipt_id)
        except Receipt.DoesNotExist:
            return Response({"error": "Receipt not found"}, status=status.HTTP_404_NOT_FOUND)

        # find-or-create customer
        customer = None
        if phone or email:
            customer_qs = Customer.objects.filter(user_client=user_client)
            if phone:
                customer = customer_qs.filter(phone=phone).first()
            if not customer and email:
                customer = customer_qs.filter(email=email).first()
            if not customer:
                customer = Customer.objects.create(
                    user_client=user_client,
                    name=phone or email or "Walk-in",
                    email=email,
                    phone=phone,
                    address="",
                )

        if not customer:
            return Response({"error": "Provide phone or email to link"}, status=status.HTTP_400_BAD_REQUEST)

        # Link on receipt and header
        receipt.customer = customer
        receipt.anonymous_customer_id = None
        receipt.save(update_fields=['customer', 'anonymous_customer_id'])

        header = receipt.sales_header
        header.customer = customer
        header.anonymous_customer_id = None
        header.save(update_fields=['customer', 'anonymous_customer_id'])

        # Update anonymous profile stats (optional: merge)
        # In phase 1, we simply clear anonymous; future phase can merge features_json.

        return Response({
            "message": "Linked receipt to customer",
            "receipt_id": str(receipt.receipt_id),
            "customer_id": str(customer.customer_id),
        }, status=status.HTTP_200_OK)


class ReceiptLinkByTokenAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Link an anonymous past receipt using its printed QR/token plus phone/email.",
        request_body=ReceiptLinkTokenSerializer,
        responses={
            200: openapi.Response(description="Linked"),
            400: openapi.Response(description="Validation error"),
            404: openapi.Response(description="Not found"),
        },
        tags=['POS Checkout']
    )
    def post(self, request):
        user_client: UserClient = request.user
        serializer = ReceiptLinkTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        token = data['token']
        phone = data.get('phone')
        email = data.get('email')

        try:
            receipt = Receipt.objects.get(link_token=token)
        except Receipt.DoesNotExist:
            return Response({"error": "Invalid token"}, status=status.HTTP_404_NOT_FOUND)

        # find-or-create customer
        customer = None
        qs = Customer.objects.filter(user_client=user_client)
        if phone:
            customer = qs.filter(phone=phone).first()
        if not customer and email:
            customer = qs.filter(email=email).first()
        if not customer:
            customer = Customer.objects.create(
                user_client=user_client,
                name=phone or email or "Walk-in",
                email=email,
                phone=phone,
                address="",
            )

        # Link on receipt and header
        receipt.customer = customer
        receipt.anonymous_customer_id = None
        receipt.save(update_fields=['customer', 'anonymous_customer_id'])

        header = receipt.sales_header
        header.customer = customer
        header.anonymous_customer_id = None
        header.save(update_fields=['customer', 'anonymous_customer_id'])

        return Response({
            "message": "Linked receipt by token",
            "receipt_id": str(receipt.receipt_id),
            "customer_id": str(customer.customer_id),
        }, status=status.HTTP_200_OK)
