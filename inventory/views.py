from django.shortcuts import render

# Create your views here.
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import Part, StockMovement


@login_required
def dashboard(request):
    # Annotate every part with its total stock in ONE database query
    parts = Part.objects.annotate(
        total=Coalesce(
            Sum("movements__quantity"),
            Value(Decimal("0")),
            output_field=DecimalField(),
        )
    )

    low_stock = parts.filter(total__lte=F("min_level")).order_by("total")
    out_of_stock_count = parts.filter(total__lte=0).count()
    stock_value = sum(p.total * p.unit_cost for p in parts if p.unit_cost)

    # Most-used parts in the last 30 days
    since = timezone.now() - timedelta(days=30)
    top_used = (
        StockMovement.objects.filter(reason="used", created_at__gte=since)
        .values("part__name")
        .annotate(used=-Sum("quantity"))
        .order_by("-used")[:5]
    )
    chart_data = {
        "labels": [row["part__name"] for row in top_used],
        "values": [float(row["used"]) for row in top_used],
    }

    recent = StockMovement.objects.select_related("part", "created_by").order_by(
        "-created_at"
    )[:8]

    context = {
        "total_items": parts.count(),
        "low_stock": low_stock,
        "low_stock_count": low_stock.count(),
        "out_of_stock_count": out_of_stock_count,
        "stock_value": stock_value,
        "chart_data": chart_data,
        "recent": recent,
    }
    return render(request, "inventory/dashboard.html", context)