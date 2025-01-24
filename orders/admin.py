from django.contrib import admin
from .models import Payment, Order, OrderFood



class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_id', 'payment_method', 'amount', 'status', 'created_at']
    search_fields = ['transaction_id', 'user__email']
    list_filter = ['payment_method', 'status', 'created_at']



class OrderFoodInline(admin.TabularInline):
    model = OrderFood
    readonly_fields = ('order', 'payment', 'user', 'fooditem', 'quantity', 'price', 'amount')
    extra = 0



class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'email',  'total', 'payment_method', 'order_placed_to']
    list_display_links = ['order_number']
    search_fields = ['order_number', 'email', 'user__email']
    list_filter = ['status', 'created_at', 'updated_at']
    inlines = [OrderFoodInline]  



class OrderFoodAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'order', 'payment', 'fooditem', 'quantity', 'amount', 'created_at', 'updated_at']
    search_fields = ['order__order_number', 'user__email', 'fooditem__food_title']
    list_filter = ['created_at', 'updated_at'] 

    def order_number(self, obj):
        
        return obj.order.order_number
    order_number.short_description = 'Order Number'


# Register models in admin site
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderFood, OrderFoodAdmin)
