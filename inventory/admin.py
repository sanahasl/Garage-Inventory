from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Part, StockMovement, PriceRecord,Order

class PriceRecordInline(admin.TabularInline):
        model = PriceRecord
        extra = 1
        
@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ("name", "part_number", "category", "stock_level", "unit", "min_level", "reorder")
    list_filter = ("category", "supplier")
    search_fields = ("name", "part_number", "location")
    inlines = [PriceRecordInline]

    @admin.display(boolean=True, description="Needs reorder")
    def reorder(self, obj):
        return obj.needs_reorder

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("created_at", "part", "quantity", "reason", "job_reference", "created_by")
    list_filter = ("reason",)
    search_fields = ("part__name", "job_reference")
    
@admin.register(Order)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ("part", "quantity", "ordered_on", "supplier", "expected_date", "note", "status")
    list_filter = ("status",)
    search_fields = ("part__name", "supplier")