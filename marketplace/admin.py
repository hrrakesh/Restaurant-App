from django.contrib import admin
from .models import Cart,Tax



class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'fooditem', 'quantity', 'updated_at')
    list_filter = ('fooditem',)

class TaxAdmin(admin.ModelAdmin):
    list_display = ('tax_type', 'tax_percentage', 'is_active')
    list_editable = ('tax_percentage', 'is_active')

     

admin.site.register(Cart, CartAdmin)
admin.site.register(Tax, TaxAdmin)