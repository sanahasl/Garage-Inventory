from django.db import models

# Create your models here.

from django.conf import settings
from django.db.models import Sum


class Part(models.Model):
    class Category(models.TextChoices):
        PART = "part", "Spare part"
        PAINT = "paint", "Paint"
        CONSUMABLE = "consumable", "Consumable"

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