from django.contrib import admin

from .models import ValueDiscount


class ValueDiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'amount', 'percentage', 'start_date', 'end_date')

admin.site.register(ValueDiscount, ValueDiscountAdmin)
