from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum


class Part(models.Model):
    class Category(models.TextChoices):
        PART = "part", "Spare part"
        PAINT = "paint", "Paint"
        CONSUMABLE = "consumable", "Consumable"
        
    @property
    def current_price(self):
        latest = self.prices.first()          # newest, because of Meta.ordering
        return latest.price if latest else self.unit_cost

    name = models.CharField(max_length=200)
    part_number = models.CharField(max_length=100, blank=True)  # or paint code
    category = models.CharField(max_length=20, choices=Category.choices)
    unit = models.CharField(max_length=20, default="pcs")  # pcs, litres, ml...
    min_level = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    location = models.CharField(max_length=100, blank=True)  # e.g. "Shelf B2"
    supplier = models.CharField(max_length=200, blank=True)  # own table later
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.part_number})" if self.part_number else self.name

    @property
    def stock_level(self):
        total = self.movements.aggregate(total=Sum("quantity"))["total"]
        return total or 0

    @property
    def needs_reorder(self):
        return self.stock_level <= self.min_level


class StockMovement(models.Model):
    class Reason(models.TextChoices):
        RECEIVED = "received", "Delivery received"
        USED = "used", "Used on job"
        ADJUSTMENT = "adjustment", "Stock-take correction"
        WASTE = "waste", "Damaged / wasted"

    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name="movements")
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # + in, - out
    reason = models.CharField(max_length=20, choices=Reason.choices)
    job_reference = models.CharField(max_length=100, blank=True)  # becomes a Job table later
    note = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.part.name}: {self.quantity:+} ({self.reason})"
    
class PriceRecord(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name="prices")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=200, blank=True)
    recorded_at = models.DateField(default=timezone.localdate)
    note = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["-recorded_at", "-id"]   # newest first

    def __str__(self):
        return f"{self.part.name}: {self.price} on {self.recorded_at}"
    
class Order(models.Model):
    class Status(models.TextChoices):
        ORDERED = "ordered", "Order Placed"
        RECEIVED = "received", "Received"
        CANCELLED = "cancelled", "Cancelled"
        OVERDUE = "overdue", "Overdue"

    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name="orders")
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length = 200, blank=True)
    ordered_on = models.DateField(default=timezone.localdate)
    expected_date = models.DateField(null=True,blank=True)
    status = models.CharField(max_length=20, choices=Status.choices)
    note = models.CharField(max_length=400, blank=True)
    
    @property
    def is_overdue(self):
        return (
            self.status == self.Status.OVERDUE
            and self.expected_date is not None
            and self.expected_date < timezone.localdate()
            )