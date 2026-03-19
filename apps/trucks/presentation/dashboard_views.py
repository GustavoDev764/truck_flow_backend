"""Views do dashboard: relatórios de caminhões (cliente e manage)."""

from __future__ import annotations

from django.db.models import Avg, Count, Sum
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek, TruncYear
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsClienteOrManage
from apps.trucks.infrastructure.persistence.django_models import TruckModel


def _truck_to_dict(obj) -> dict | None:
    if obj is None:
        return None
    return {
        "id": str(obj.id),
        "license_plate": obj.license_plate,
        "brand": obj.brand,
        "model": obj.model_name,
        "manufacturing_year": obj.manufacturing_year,
        "fipe_price": str(obj.fipe_price),
    }


class DashboardAPIView(APIView):
    """Relatórios: caminhão mais caro/barato, valor médio, linha do tempo por período."""

    permission_classes = [IsClienteOrManage]

    def get(self, request):

        cheapest = TruckModel.objects.order_by("fipe_price").first()
        most_expensive = TruckModel.objects.order_by("-fipe_price").first()

        avg_result = TruckModel.objects.aggregate(avg=Avg("fipe_price"))
        average_value = float(avg_result["avg"] or 0)

        period = request.query_params.get("period", "month")

        trunc_func = {
            "day": TruncDate("created_at"),
            "week": TruncWeek("created_at"),
            "month": TruncMonth("created_at"),
            "year": TruncYear("created_at"),
        }.get(period, TruncMonth("created_at"))

        timeline_qs = (
            TruckModel.objects.annotate(period=trunc_func)
            .values("period")
            .annotate(total=Sum("fipe_price"), count=Count("id"))
            .order_by("period")
        )

        timeline = []
        for row in timeline_qs:
            dt = row["period"]
            if dt:
                if period == "year":
                    label = str(dt.year)
                elif period == "month":
                    label = dt.strftime("%Y-%m")
                elif period == "week":
                    label = dt.strftime("%Y-%m-%d")
                else:
                    label = dt.strftime("%Y-%m-%d") if hasattr(dt, "strftime") else str(dt)[:10]
            else:
                label = ""
            timeline.append(
                {
                    "period": label,
                    "total": float(row["total"] or 0),
                    "count": row["count"],
                }
            )

        return Response(
            {
                "cheapest_truck": _truck_to_dict(cheapest) if cheapest else None,
                "most_expensive_truck": _truck_to_dict(most_expensive) if most_expensive else None,
                "average_value": round(average_value, 2),
                "total_trucks": TruckModel.objects.count(),
                "timeline": timeline,
            }
        )
