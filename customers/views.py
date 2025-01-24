from django.shortcuts import get_object_or_404, redirect, render
from accounts.models import  UserProfile
from accounts.views import login_required, user_passes_test, check_role_customer
from accounts.forms import UserProfileForm, UserInfoForm
from django.contrib import messages
import simplejson as json
from orders.models import Order, OrderFood
from django.core.paginator import Paginator




@login_required(login_url='login')
@user_passes_test(check_role_customer)
def customer_profile(request):


    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            user_form.save()
            profile.save()
            messages.success(request, 'Profile Updated')
            return redirect('customer-profile')
        else:
            print(user_form.errors)
            print(profile_form.errors)
            messages.error(request, 'Something went wrong!')
            return redirect('customer-profile')

    else:
        profile_form = UserProfileForm(instance = profile)
        user_form = UserInfoForm(instance = request.user)

    context = {
        'page_title': 'customer-profile',
        'profile_form': profile_form,
        'user_form': user_form,
        'profile': profile,
    }

    return render(request, 'customers/customer-profile.html',context)


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def my_orders(request):


    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')

    paginator = Paginator(orders, 5) 

    page_number = request.GET.get('page')  # Get the current page number from the URL
    page_orders = paginator.get_page(page_number)  # Get the orders for the current page

    context  ={
        'page_title': 'my-orders',
        'orders': page_orders,
        'orders_count': orders.count()
    }
    return render(request, 'customers/my-order.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def order_details(request, order_number):

    try:
        order = Order.objects.get(user=request.user, order_number=order_number, is_ordered=True)
        ordered_food = OrderFood.objects.filter(order=order)
        sub_total = 0
        for item in ordered_food:
            sub_total += item.price * item.quantity
        tax_data = json.loads(order.tax_data)

        context = {
            'order': order,
            'ordered_food': ordered_food,
            'page_title': 'my-order-'+order_number,
            'sub_total':round(sub_total,2),
            'tax_data': tax_data,

        }
        return render(request, 'customers/order-details.html', context)


    except Exception as e:
        print(e)

    context = {
            'page_title': 'my-order-'+order_number,

        }
    return render(request, 'customers/order-details.html', context)
