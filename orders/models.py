from django.db import models
from accounts.models import User
from menu.models import FoodItem
from vendor.models import Vendor
import simplejson as json
# Create your models here.

request_object =''

class Payment(models.Model):
    PAYMENT_METHOD = (
        ('Paypal', 'Paypal'),
        ('RazorPay', 'RazorPay'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100)
    amount = models.CharField(max_length=10)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = "Payments's"

    def __str__(self):
        return self.transaction_id
    
class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    vendors = models.ManyToManyField(Vendor, blank=True)
    order_number = models.CharField(max_length=50)
    first_name = models.CharField(max_length=10)
    last_name = models.CharField(max_length=10)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=200)
    country = models.CharField(max_length=15, blank=True)
    state = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=15)
    pin_code = models.CharField(max_length=10)
    total = models.FloatField()
    tax_data = models.JSONField(blank=True, help_text= "Data Format: {'tax_type':{'tax_percentage': 'tax_amount'}}", null=True)
    total_data = models.JSONField(blank=True, null=True)
    total_tax = models.FloatField()
    payment_method = models.CharField(max_length=25)
    status = models.CharField(choices=STATUS, max_length=20, default='New')
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = "Order's"

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_total_by_vendor(self):
        vendor = Vendor.objects.get(user=request_object.user)
        
        if self.total_data:
            total_data = json.loads(self.total_data)
            data = total_data.get(str(vendor.id))

        subtotal = 0
        tax = 0
        tax_dict = {}
        context = None
        if data:
            key, val = next(iter(data.items()))

            subtotal += float(key)  
            tax_dict.update(val)  

            for i in val:  
                for j in val[i]:
                    tax += float(val[i][j])  

            grand_total = float(subtotal) + float(tax)

            context = {
                'subtotal': subtotal,
                'tax_dict': tax_dict,
                'grand_total': grand_total,
            }

        return context


    def order_placed_to(self):
        return ', '.join([str(i) for i in self.vendors.all()])

    def __str__(self):
        return self.order_number
    
class OrderFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fooditem.food_title
