from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import transaction
from .models import PurchaseHeader, PurchaseDetail, Payment, PurchaseOrderHeader, PurchaseOrderDetail, GRNHeader, GRNDetail
from .serializers import (
    PurchaseHeaderSerializer, PurchaseDetailSerializer, PaymentSerializer,
    PurchaseOrderHeaderSerializer, PurchaseOrderDetailSerializer, GRNHeaderSerializer, GRNDetailSerializer,
    PurchaseOrderCreateSerializer, PurchaseOrderConvertSerializer, GenerateGRNSerializer,
    PurchaseOrderHeaderFullSerializer, PurchaseHeaderFullSerializer,
    PurchaseOrderFullUpdateSerializer, PurchaseFullUpdateSerializer
)
from registry.models import Supplier, PaymentOption
from products.models import Product, Unit
from users.models import UserClient
import uuid
from Domain.models import AuditLog
from authentication.permissions import IsOwner, IsManager, IsEmployee
from rest_framework.permissions import IsAuthenticated

@swagger_auto_schema(tags=["Purchases"]) 
class PurchaseHeaderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseHeader.objects.all()
    serializer_class = PurchaseHeaderSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action='VOID',
            model_name='PurchaseHeader',
            object_id=str(instance.purchase_header_id),
            reason=request.data.get('reason') if hasattr(request, 'data') else None,
            before_data={'invoice_number': instance.invoice_number, 'total_cost': float(instance.total_cost)},
            after_data=None
        )
        return response
    permission_classes = [IsAuthenticated, IsManager]  # Allow all roles to access this view

class PurchaseDetailViewSet(viewsets.ModelViewSet):
    queryset = PurchaseDetail.objects.all()
    serializer_class = PurchaseDetailSerializer
    permission_classes = [IsAuthenticated, IsManager]  # Allow all roles to access this view

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

@swagger_auto_schema(tags=["Purchase Orders"]) 
class PurchaseOrderHeaderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrderHeader.objects.all()
    serializer_class = PurchaseOrderHeaderSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user if self.request.user.is_authenticated else None,
            action='CREATE',
            model_name='PurchaseOrderHeader',
            object_id=str(instance.po_header_id),
            reason='PO created',
            before_data=None,
            after_data={'order_number': instance.order_number, 'supplier': str(instance.supplier_id)}
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action='VOID',
            model_name='PurchaseOrderHeader',
            object_id=str(instance.po_header_id),
            reason=request.data.get('reason') if hasattr(request, 'data') else None,
            before_data={'order_number': instance.order_number},
            after_data=None
        )
        return response

@swagger_auto_schema(tags=["Purchase Orders"]) 
class PurchaseOrderDetailViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrderDetail.objects.all()
    serializer_class = PurchaseOrderDetailSerializer


class PurchaseOrderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a Purchase Order header with details in one request.",
        request_body=PurchaseOrderCreateSerializer,
        responses={201: openapi.Response(description="PO created"), 400: openapi.Response(description="Validation error")},
        tags=['Purchase Orders']
    )
    @transaction.atomic
    def post(self, request):
        serializer = PurchaseOrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        user_client: UserClient = request.user
        supplier = Supplier.objects.get(pk=data['supplier_id'])

        order_number = f"PO-{uuid.uuid4().hex[:8].upper()}"
        po_header = PurchaseOrderHeader.objects.create(
            user_client=user_client,
            supplier=supplier,
            order_number=order_number,
            expected_date=data.get('expected_date'),
            notes=data.get('notes') or ''
        )

        for item in data['items']:
            product = Product.objects.get(pk=item['product_id'])
            unit = Unit.objects.get(pk=item['unit_id'])
            PurchaseOrderDetail.objects.create(
                user_client=user_client,
                po_header=po_header,
                product=product,
                unit=unit,
                quantity=item['quantity'],
                price_per_unit=item['price_per_unit'],
            )

        return Response({
            'po_header_id': str(po_header.po_header_id),
            'order_number': po_header.order_number,
        }, status=status.HTTP_201_CREATED)


class PurchaseOrderRetrieveHeaderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a Purchase Order header by ID (header only).",
        responses={200: openapi.Response(description="OK"), 404: openapi.Response(description="PO not found")},
        tags=['Purchase Orders']
    )
    def get(self, request, po_header_id):
        try:
            po = PurchaseOrderHeader.objects.get(pk=po_header_id)
        except PurchaseOrderHeader.DoesNotExist:
            return Response({'error': 'PO not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PurchaseOrderHeaderSerializer(po).data, status=status.HTTP_200_OK)


class PurchaseOrderRetrieveFullAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a Purchase Order with all details by ID (header + details).",
        responses={200: openapi.Response(description="OK"), 404: openapi.Response(description="PO not found")},
        tags=['Purchase Orders']
    )
    def get(self, request, po_header_id):
        try:
            po = PurchaseOrderHeader.objects.get(pk=po_header_id)
        except PurchaseOrderHeader.DoesNotExist:
            return Response({'error': 'PO not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PurchaseOrderHeaderFullSerializer(po).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a Purchase Order header and its details atomically.",
        request_body=PurchaseOrderFullUpdateSerializer,
        responses={200: openapi.Response(description="PO updated"), 404: openapi.Response(description="PO not found")},
        tags=['Purchase Orders']
    )
    @transaction.atomic
    def put(self, request, po_header_id):
        try:
            po = PurchaseOrderHeader.objects.select_for_update().get(pk=po_header_id)
        except PurchaseOrderHeader.DoesNotExist:
            return Response({'error': 'PO not found'}, status=status.HTTP_404_NOT_FOUND)

        update_serializer = PurchaseOrderFullUpdateSerializer(data=request.data)
        if not update_serializer.is_valid():
            return Response(update_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = update_serializer.validated_data

        # Update header fields
        if 'expected_date' in data:
            po.expected_date = data['expected_date']
        if 'notes' in data:
            po.notes = data['notes']
        po.save()

        user_client: UserClient = request.user
        # Process detail operations
        for item in data.get('details', []):
            if item.get('delete'):
                # Delete by id
                if item.get('po_detail_id'):
                    PurchaseOrderDetail.objects.filter(pk=item['po_detail_id'], po_header=po).delete()
                continue
            # Upsert: by id if provided, else create
            if item.get('po_detail_id'):
                try:
                    pod = PurchaseOrderDetail.objects.get(pk=item['po_detail_id'], po_header=po)
                except PurchaseOrderDetail.DoesNotExist:
                    return Response({'error': f"PO detail not found: {item['po_detail_id']}"}, status=status.HTTP_400_BAD_REQUEST)
                if item.get('product_id'):
                    pod.product = Product.objects.get(pk=item['product_id'])
                if item.get('unit_id'):
                    pod.unit = Unit.objects.get(pk=item['unit_id'])
                pod.quantity = item['quantity']
                pod.price_per_unit = item['price_per_unit']
                pod.save()
            else:
                product = Product.objects.get(pk=item['product_id']) if item.get('product_id') else None
                unit = Unit.objects.get(pk=item['unit_id']) if item.get('unit_id') else None
                if not product or not unit:
                    return Response({'error': 'product_id and unit_id required for new detail'}, status=status.HTTP_400_BAD_REQUEST)
                PurchaseOrderDetail.objects.create(
                    user_client=user_client,
                    po_header=po,
                    product=product,
                    unit=unit,
                    quantity=item['quantity'],
                    price_per_unit=item['price_per_unit'],
                )

        return Response(PurchaseOrderHeaderFullSerializer(po).data, status=status.HTTP_200_OK)


class PurchaseOrderConvertAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Convert an existing PO to a Purchase (invoice) with details.",
        request_body=PurchaseOrderConvertSerializer,
        responses={201: openapi.Response(description="Purchase created"), 404: openapi.Response(description="PO not found")},
        tags=['Purchase Orders']
    )
    @transaction.atomic
    def post(self, request, po_header_id):
        serializer = PurchaseOrderConvertSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data

        try:
            with transaction.atomic():
                po = PurchaseOrderHeader.objects.select_for_update().get(pk=po_header_id)
                # Prevent duplicate conversions
                if po.converted_purchase_id:
                    return Response(
                        {
                            'error': 'PO already converted',
                            'purchase_header_id': str(po.converted_purchase_id),
                        },
                        status=status.HTTP_409_CONFLICT,
                    )
        except PurchaseOrderHeader.DoesNotExist:
            return Response({'error': 'PO not found'}, status=status.HTTP_404_NOT_FOUND)

        user_client: UserClient = request.user
        payment_option = None
        if data.get('payment_option_id'):
            try:
                payment_option = PaymentOption.objects.get(pk=data['payment_option_id'])
            except PaymentOption.DoesNotExist:
                return Response({'error': 'Invalid payment_option_id'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            payment_option = PaymentOption.objects.filter(user_client=user_client, name__iexact='Cash').first() or PaymentOption.objects.filter(user_client=user_client).first()

        subtotal = 0
        for d in po.po_details.all():
            subtotal += float(d.quantity) * float(d.price_per_unit)
        total_cost = subtotal
        remaining_balance = total_cost

        order_number = f"PU-{uuid.uuid4().hex[:8].upper()}"
        invoice_number = data.get('invoice_number') or f"INV-{uuid.uuid4().hex[:8].upper()}"
        purchase_header = PurchaseHeader.objects.create(
            user_client=user_client,
            supplier=po.supplier,
            payment_option=payment_option,
            order_number=order_number,
            invoice_number=invoice_number,
            subtotal=subtotal,
            total_cost=total_cost,
            remaining_balance=remaining_balance,
        )

        for d in po.po_details.all():
            PurchaseDetail.objects.create(
                purchase_header=purchase_header,
                user_client=user_client,
                product=d.product,
                unit=d.unit,
                quantity=d.quantity,
                price_per_unit=d.price_per_unit,
                discount=0,
            )

        # Mark PO as converted to this Purchase
        po.converted_purchase = purchase_header
        po.save(update_fields=['converted_purchase'])

        return Response({
            'purchase_header_id': str(purchase_header.purchase_header_id),
            'order_number': purchase_header.order_number,
            'invoice_number': purchase_header.invoice_number,
        }, status=status.HTTP_201_CREATED)


class PurchaseRetrieveHeaderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a Purchase header by ID (header only).",
        responses={200: openapi.Response(description="OK"), 404: openapi.Response(description="Purchase not found")},
        tags=['Purchases']
    )
    def get(self, request, purchase_header_id):
        try:
            purchase = PurchaseHeader.objects.get(pk=purchase_header_id)
        except PurchaseHeader.DoesNotExist:
            return Response({'error': 'Purchase not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PurchaseHeaderSerializer(purchase).data, status=status.HTTP_200_OK)


class PurchaseRetrieveFullAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a Purchase with all details by ID (header + details).",
        responses={200: openapi.Response(description="OK"), 404: openapi.Response(description="Purchase not found")},
        tags=['Purchases']
    )
    def get(self, request, purchase_header_id):
        try:
            purchase = PurchaseHeader.objects.get(pk=purchase_header_id)
        except PurchaseHeader.DoesNotExist:
            return Response({'error': 'Purchase not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PurchaseHeaderFullSerializer(purchase).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a Purchase header and its details atomically.",
        request_body=PurchaseFullUpdateSerializer,
        responses={200: openapi.Response(description="Purchase updated"), 404: openapi.Response(description="Purchase not found")},
        tags=['Purchases']
    )
    @transaction.atomic
    def put(self, request, purchase_header_id):
        try:
            purchase = PurchaseHeader.objects.select_for_update().get(pk=purchase_header_id)
        except PurchaseHeader.DoesNotExist:
            return Response({'error': 'Purchase not found'}, status=status.HTTP_404_NOT_FOUND)

        update_serializer = PurchaseFullUpdateSerializer(data=request.data)
        if not update_serializer.is_valid():
            return Response(update_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = update_serializer.validated_data

        user_client: UserClient = request.user
        # Update header fields
        if data.get('payment_option_id'):
            try:
                purchase.payment_option = PaymentOption.objects.get(pk=data['payment_option_id'])
            except PaymentOption.DoesNotExist:
                return Response({'error': 'Invalid payment_option_id'}, status=status.HTTP_400_BAD_REQUEST)
        if 'invoice_number' in data:
            purchase.invoice_number = data['invoice_number']
        purchase.save()

        # Process detail operations
        subtotal = 0
        for item in data.get('details', []):
            if item.get('delete'):
                if item.get('purchase_detail_id'):
                    PurchaseDetail.objects.filter(pk=item['purchase_detail_id'], purchase_header=purchase).delete()
                continue
            if item.get('purchase_detail_id'):
                try:
                    pd = PurchaseDetail.objects.get(pk=item['purchase_detail_id'], purchase_header=purchase)
                except PurchaseDetail.DoesNotExist:
                    return Response({'error': f"Purchase detail not found: {item['purchase_detail_id']}"}, status=status.HTTP_400_BAD_REQUEST)
                if item.get('product_id'):
                    pd.product = Product.objects.get(pk=item['product_id'])
                if item.get('unit_id'):
                    pd.unit = Unit.objects.get(pk=item['unit_id'])
                pd.quantity = item['quantity']
                pd.price_per_unit = item['price_per_unit']
                pd.discount = item.get('discount', pd.discount)
                pd.save()
                subtotal += float(pd.quantity) * float(pd.price_per_unit) - float(pd.discount or 0)
            else:
                product = Product.objects.get(pk=item['product_id']) if item.get('product_id') else None
                unit = Unit.objects.get(pk=item['unit_id']) if item.get('unit_id') else None
                if not product or not unit:
                    return Response({'error': 'product_id and unit_id required for new detail'}, status=status.HTTP_400_BAD_REQUEST)
                pd = PurchaseDetail.objects.create(
                    purchase_header=purchase,
                    user_client=user_client,
                    product=product,
                    unit=unit,
                    quantity=item['quantity'],
                    price_per_unit=item['price_per_unit'],
                    discount=item.get('discount', 0),
                )
                subtotal += float(pd.quantity) * float(pd.price_per_unit) - float(pd.discount or 0)

        # Recompute totals (business rules may vary)
        purchase.subtotal = subtotal
        purchase.total_cost = subtotal
        # Keep remaining_balance logic simple: equals total_cost unless payments applied elsewhere
        purchase.remaining_balance = purchase.total_cost
        purchase.save()

        return Response(PurchaseHeaderFullSerializer(purchase).data, status=status.HTTP_200_OK)


class PurchaseGenerateGRNAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Generate a GRN from a Purchase header (no auto-generation).",
        request_body=GenerateGRNSerializer,
        responses={201: openapi.Response(description="GRN created"), 404: openapi.Response(description="Purchase not found")},
        tags=['GRNs']
    )
    @transaction.atomic
    def post(self, request, purchase_header_id):
        serializer = GenerateGRNSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data

        try:
            purchase = PurchaseHeader.objects.get(pk=purchase_header_id)
        except PurchaseHeader.DoesNotExist:
            return Response({'error': 'Purchase not found'}, status=status.HTTP_404_NOT_FOUND)

        user_client: UserClient = request.user
        grn_header = GRNHeader.objects.create(
            user_client=user_client,
            supplier=purchase.supplier,
            po_header=None,
            purchase_header=purchase,
            grn_number=data['grn_number'],
            notes=f"GRN for purchase {purchase.order_number}"
        )

        for pd in purchase.purchase_details.all():
            GRNDetail.objects.create(
                user_client=user_client,
                grn_header=grn_header,
                product=pd.product,
                unit=pd.unit,
                quantity=pd.quantity,
                price_per_unit=pd.price_per_unit,
            )

        return Response({
            'grn_header_id': str(grn_header.grn_header_id),
            'grn_number': grn_header.grn_number,
        }, status=status.HTTP_201_CREATED)

@swagger_auto_schema(tags=["GRNs"])
class GRNHeaderViewSet(viewsets.ModelViewSet):
    queryset = GRNHeader.objects.all()
    serializer_class = GRNHeaderSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user if self.request.user.is_authenticated else None,
            action='CREATE',
            model_name='GRNHeader',
            object_id=str(instance.grn_header_id),
            reason='GRN created',
            before_data=None,
            after_data={'grn_number': instance.grn_number, 'supplier': str(instance.supplier_id)}
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action='VOID',
            model_name='GRNHeader',
            object_id=str(instance.grn_header_id),
            reason=request.data.get('reason') if hasattr(request, 'data') else None,
            before_data={'grn_number': instance.grn_number},
            after_data=None
        )
        return response

@swagger_auto_schema(tags=["GRNs"])
class GRNDetailViewSet(viewsets.ModelViewSet):
    queryset = GRNDetail.objects.all()
    serializer_class = GRNDetailSerializer
    permission_classes = [IsAuthenticated, IsManager]  # Allow all roles to access this view