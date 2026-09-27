from django.shortcuts import render

# Create your views here.
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, F, Sum, Value, Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import Part, StockMovement

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .forms import StockAdjustForm
from .models import Order, PriceRecord


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



@login_required
def part_list(request):
    query = request.GET.get("q", "").strip()

    parts = Part.objects.annotate(
        total=Coalesce(
            Sum("movements__quantity"),
            Value(Decimal("0")),
            output_field=DecimalField(),
        )
    ).order_by("name")

    if query:
        parts = parts.filter(
            Q(name__icontains=query) | Q(part_number__icontains=query) | Q(id__iexact=query)
        )

    context = {
        "parts": parts,
        "query": query,
    }
    return render(request, "inventory/parts.html", context)

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .forms import StockAdjustForm
from .models import Order, PriceRecord


@login_required
def part_detail(request, pk):
    part = Part.objects.annotate(
        total=Coalesce(
            Sum("movements__quantity"),
            Value(Decimal("0")),
            output_field=DecimalField(),
        )
    ).get(pk=pk)

    movements = part.movements.select_related("created_by").order_by("-created_at")[:15]
    prices = part.prices.all()[:10]
    orders = part.orders.all()

    context = {
        "part": part,
        "movements": movements,
        "prices": prices,
        "orders": orders,
    }
    return render(request, "inventory/part_detail.html", context)


@login_required
def adjust_stock(request, pk):
    part = get_object_or_404(Part, pk=pk)

    if request.method == "POST":
        form = StockAdjustForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data["quantity"]
            taking_out = form.cleaned_data["action"] == "out"

            StockMovement.objects.create(
                part=part,
                quantity=-qty if taking_out else qty,
                reason="used" if taking_out else "received",
                job_reference=form.cleaned_data["job_reference"],
                created_by=request.user,
            )
            verb = "Removed" if taking_out else "Added"
            messages.success(request, f"{verb} {qty} {part.unit} of {part.name}.")
            return redirect("part_detail", pk=part.pk)
    else:
        form = StockAdjustForm()

    return render(request, "inventory/adjust_stock.html", {"part": part, "form": form})