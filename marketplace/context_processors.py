from .models import Cart, Tax
from menu.models import FoodItem


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
            else:
                cart_count = 0 
        except:
            cart_count = 0
    return dict(cart_count=cart_count)

def get_cart_amount(request):
    subtotal = 0
    tax = 0
    grand_total = 0
    tax_dict = None
    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(user=request.user)
        for item in cart_item:
            food_item = FoodItem.objects.get(pk=item.fooditem.id)
            subtotal += (food_item.price * item.quantity)
        
        get_tax = Tax.objects.filter(is_active=True)
        tax_dict = {}
        
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((subtotal * (tax_percentage/100)),2)
            tax_dict[tax_type] = {str(tax_percentage):tax_amount}  # must convert decimal to str
        
       
        for  tax_value in tax_dict.values():
            for  tax_amount in tax_value.values():
                tax = tax + tax_amount
        
        
        grand_total = subtotal + tax 
    return dict(subtotal=subtotal, tax=tax, grand_total=grand_total, tax_dict=tax_dict)