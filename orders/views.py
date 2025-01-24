from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from accounts.models import User
from marketplace.models import Cart, Tax
from marketplace.context_processors import get_cart_amount
from menu.models import FoodItem
from .forms import OrderForm
from .models import Order, OrderFood, Payment
import simplejson as json
from .utils import generate_order_number, get_one_usd
from django.contrib import messages
from accounts.utils import send_notification
from django.contrib.auth.decorators import login_required
from foodonline_main.settings import RZP_KEY_ID, RZP_KEY_SECRET, USE_PAY_PAL, USE_RAZOR_PAY


#razor_pay implementation
import razorpay

if USE_RAZOR_PAY:
    try:
        client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))
        
    except Exception as e:
        print("Why razorapy failed: ",e)




@login_required(login_url='login')
def place_order(request):
    
    if request.user.role == 1:
  
        cart_items = Cart.objects.filter(user=request.user)  
        if cart_items.exists():
            messages.success(request, "Cart Cleared")

            cart_items.delete()  

        messages.warning(request, "Currently, we are not accepting orders from Vendor accounts.")
        Order.objects.filter(user=request.user, is_ordered=False).delete() 
        return redirect('home')

    
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    
    vendors_id = []
    for i in cart_items:
        if i.fooditem.vendor.id not in vendors_id:
            vendors_id.append(i.fooditem.vendor.id)

    get_tax = Tax.objects.filter(is_active=True)
    subtotal = 0
    k = {}
    total_data = {}
    for i in cart_items:
        fooditem = FoodItem.objects.get(pk=i.fooditem.id, vendor_id__in=vendors_id)
        v_id = fooditem.vendor.id
        if v_id in k:
            subtotal = k[v_id]
            subtotal += fooditem.price * i.quantity
            k[v_id] = subtotal
        else:
            subtotal = fooditem.price * i.quantity
            k[v_id] = subtotal
        
        # calculate tax amount:
        tax_dict = {}
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round(  ( ( tax_percentage * subtotal) / 100), 2)
            tax_dict.update({tax_type: {str(tax_percentage): str(tax_amount)}})
        

        total_data.update({fooditem.vendor.id: {str(subtotal):tax_dict}})


    subtotal = get_cart_amount(request)['subtotal']
    total_tax = get_cart_amount(request)['tax']
    grand_total = get_cart_amount(request)['grand_total']
    tax_data = get_cart_amount(request)['tax_dict']

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']

            order.user = request.user
            order.total = grand_total
            
            order.tax_data = json.dumps(tax_data)
            order.total_data = json.dumps(total_data)
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method']
            order.save()
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_id)
            order.save()
            # for razor pay server-order creating
            # razor pay only 
            if USE_RAZOR_PAY:
                try:
                    one_usd = get_one_usd()
                    DATA = {
                        "amount": int((float(order.total) * one_usd)*100),  # Razorpay accepts only paise
                        "currency": "INR",
                        "receipt": "receipt #" + order.order_number,
                        "notes": {
                            "key1": "Nothing ",
                            "key2": "Absolute Demo Project rocky",
                        }
                    }
                    rzp_order = client.order.create(data=DATA)
                    rzp_order_id = rzp_order['id']
                except Exception as e:
                    print(f"Failed to create the order of order no: {order.order_number}")
                    print(f"Error details: {e}")
                    rzp_order_id = '' # avoiding any runtime error
                    messages.error(request, 'Something went wrong please other method or contact customer care')
                    return redirect('home')


            
            use_pay_pal = USE_PAY_PAL
            use_razor_pay = USE_RAZOR_PAY
            context ={
                'order':order,
                'cart_items': cart_items,
                'page_title': 'place-order'+'-'+ order.order_number,

                'use_pay_pal':use_pay_pal,
                'use_razor_pay':use_razor_pay,

                # sending razor pay order details
                'rzp_order_id':rzp_order_id,
                'RZP_KEY_ID': RZP_KEY_ID,
                'rzp_amount':int((float(order.total) * one_usd)*100),
            }
            return render(request,'orders/place-order.html', context)


        else:
            print(form.errors)
    
    context = {
        'page_title': 'place-order',
        
    }
    return render(request, 'orders/place-order.html', context)



@login_required(login_url='login')
def payments(request):

    use_pay_pal = USE_PAY_PAL 
    if use_pay_pal:
        
        if request.headers.get('x-requested-with', '').lower() == 'xmlhttprequest' and request.method == 'POST': # ajax
            order_number = request.POST.get('order_number')
            transaction_id = request.POST.get('transaction_id')
            payment_method = request.POST.get('payment_method')
            status = request.POST.get('status')
            

            order = Order.objects.get(user=request.user, order_number=order_number)
            payment = Payment(
                user = request.user,
                transaction_id = transaction_id,
                payment_method = payment_method,
                amount = order.total,
                status = status,

            )
            payment.save()
            #update order
            order.payment = payment
            order.is_ordered = True
            order.save()

            cart_items = Cart.objects.filter(user=request.user)
            for items in cart_items:
                ordered_food = OrderFood()
                ordered_food.order = order
                ordered_food.payment = payment
                ordered_food.user = request.user
                ordered_food.fooditem = items.fooditem
                ordered_food.quantity = items.quantity
                ordered_food.price = items.fooditem.price
                ordered_food.amount = items.fooditem.price * items.quantity
                ordered_food.save()
            

            # sending the confiramtion mail for customer
            try:
                mail_subject = 'Thank you for ordering with us'
                mail_template = 'orders/order-confirmation-email.html'
                context = {
                    'user': request.user,
                    'order': order,
                    'to_email': order.email,
                }
                send_notification(mail_subject, mail_template, context)

                

            except Exception as e:
                print(e)

            

            # send email for vendors
            to_emails = []
            cart_contianer = {}
            for i in cart_items:
                vendor_email = str(i.fooditem.vendor.user.email)
                if i.fooditem.vendor.user.email not in to_emails:
                    to_emails.append(i.fooditem.vendor.user.email)
                    cart_contianer[vendor_email] = []
                
                cart_contianer[vendor_email].append({
                    'food_item': i.fooditem.food_title,
                    'food_quantity': i.quantity,
                    'food_price': float(i.fooditem.price),
                    'food_item_price': i.quantity * float(i.fooditem.price),
                }) 

            for key, value in cart_contianer.items():
                sum_total = 0
                for v in value:
                    sum_total += v['food_item_price']
                cart_contianer[key].append({
                    'sum_total': sum_total,
                    'SGST': round(sum_total * (7/100),2),
                    'CGST': round(sum_total * (9/100),2),
                    'TOTAL_TAX_ON_YOUR_ORDER': round((round(sum_total * (7/100),2) + round(sum_total * (9/100),2)),2),
                }) 
                        
            total_vendors_found = len(to_emails)
            
            for count , email in enumerate(to_emails, start=1):
                email = email
                vendor = User.objects.get(email=email, role=1)
                try:

                    mail_subject = 'You have received new order'
                    mail_template = 'orders/new-order-received-email.html'
                    cart_items = cart_contianer[email][:-1]
                    price_value = cart_contianer[email][-1]

                    context = {
                        'vendor_name': vendor.first_name,
                        'vendor_list_order_queue': f"{count}/{total_vendors_found}",
                        'order': order,
                        'to_email': email,
                        'price_value':price_value,
                        'cart_items':cart_items,
                    }
                    send_notification(mail_subject, mail_template, context)

                except Exception as e:
                    print("Email: went wrong on this",vendor.first_name)

            
            # clear cart and delete order with is_ordered_false
            
            Cart.objects.filter(user=request.user).delete()
            Order.objects.filter(is_ordered=False).delete() # make sure no other have is_order is not False
            
            
            response = {
                'order_number': order_number,
                'transaction_id': transaction_id,
            }
            return JsonResponse(response)


@login_required(login_url='login')
def order_complete(request):

    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')
    
    user_email = request.user.email
    
    try:
        # Check if the order exists and belongs to the authenticated user
        order = Order.objects.get(
            order_number=order_number,
            payment__transaction_id=transaction_id,
            is_ordered=True,
            user__email=user_email  
        )
        
    except Order.DoesNotExist:
        messages.warning(request,'No orders found with the details')
        return redirect('home')

    try:
        print(request.user.email)
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderFood.objects.filter(order=order)
        
        sub_total = 0
        for item in ordered_food:
            sub_total += item.price * item.quantity

        tax_data = json.loads(order.tax_data)
        context = {
            'order':order,
            'ordered_food': ordered_food,
            'page_title': 'order-details',
            'sub_total': round(sub_total,2),
            'tax_data': tax_data,
        }
        return render(request, 'orders/order-complete.html', context)

    except:
        messages.warning(request,'No orders found with the details')
        return redirect('home')