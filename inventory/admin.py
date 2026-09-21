from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Part, StockMovement


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ("name", "part_number", "category", "stock_level", "unit", "min_level", "reorder")
    list_filter = ("category", "supplier")
    search_fields = ("name", "part_number", "location")

    @admin.display(boolean=True, description="Needs reorder")
    def reorder(self, obj):
        return obj.needs_reorder


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("created_at", "part", "quantity", "reason", "job_reference", "created_by")
    list_filter = ("reason",)
    search_fields = ("part__name", "job_reference")