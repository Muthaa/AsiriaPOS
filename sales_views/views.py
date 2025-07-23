from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated  # Change if you want to restrict access
from django.utils.timezone import now
from django.db.models import Sum
from sales.models import SalesHeader  # or asiripos.models if different

class TodaysSalesTotalAPIView(APIView):
    permission_classes = [IsAuthenticated]  # ⚠️ For testing; use IsAuthenticated in production

    def get(self, request):
        today = now().date()
        total_sales = SalesHeader.objects.filter(created_at__date=today).aggregate(
            total=Sum("total_price")
        )["total"] or 0

        return Response({"total_sales": float(total_sales)})
