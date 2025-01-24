from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from accounts.models import UserProfile
from .context_processors import get_cart_amount, get_cart_counter
from .models import Cart
from menu.models import Category, FoodItem
from vendor.models import Vendor, OpeningHours
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from datetime import date, datetime
from orders.forms import OrderForm
from foodonline_main.settings import  USE_PAY_PAL, USE_RAZOR_PAY



def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True, user_profile__profile_picture__isnull=False)
    vender_count = vendors.count()
    
    context={
        'page_title': 'marketplace',
        'vendors': vendors,
        'vendor_count': vender_count,
    }
    return render(request, 'marketplace/listings.html', context)


def vendor_details(request, vendor_slug):

    vendor = get_object_or_404(Vendor, slug=vendor_slug)

    # actually we are reverse lookup on Fooditems
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )
    
    opening_hours = OpeningHours.objects.filter(vendor=vendor).order_by('day', '-from_hours')
    today_date = date.today()
    today = today_date.isoweekday()
    
    current_opening_hours = OpeningHours.objects.filter(vendor=vendor, day=today).first()
    current_opening_hours_check = OpeningHours.objects.filter(vendor=vendor, day=today)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    is_open = None
    for i in current_opening_hours_check:
        start = str(datetime.strptime(i.from_hours, "%I:%M %p").time())
        end = str(datetime.strptime(i.to_hours, "%I:%M %p").time())
       
        if current_time > start and  current_time < end:
            is_open = True
            is_open = not(i.is_holiday) and is_open
            break
        else:
            is_open = False
    

        
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'page_title':'vendor-details',
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_opening_hours':current_opening_hours,
        'is_open': is_open,
    }
    return render(request, 'marketplace/vendor-details.html', context)


def add_to_cart(request, food_id=None):

    if request.user.is_authenticated:
        
        if request.headers.get('x-requested-with', '').lower() == 'xmlhttprequest':
            #check if fooditem exist
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # check whether the fooditem added to the cart
                try:
                    check_cart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    # increase the cart quantity
                    if check_cart.quantity < 10:
                        check_cart.quantity += 1
                        check_cart.save()
                        return JsonResponse({'status':'Success', 'message': 'Increased the cart Quantity', 'cart_counter': get_cart_counter(request), 'qty': check_cart.quantity, 'cart_amount': get_cart_amount(request)})
                    else:
                        return JsonResponse({'status':'Failed', 'message': 'We are allowing max of 10 items on each category'})

                except:
                    check_cart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status':'Success', 'message': 'Added the food to the cart Quantity','cart_counter': get_cart_counter(request), 'qty': check_cart.quantity, 'cart_amount': get_cart_amount(request)})

            except:
                return JsonResponse({'status':'Failed', 'message': 'This food doesnot exist'})
        else:
            return JsonResponse({'status':'Failed', 'message': 'Invalid Response'})
    else:
        return JsonResponse({'status':'login_required', 'message': 'Please Login to continue'})


def decrease_cart(request, food_id):
    
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with', '').lower() == 'xmlhttprequest':
            #check if fooditem exist
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # check whether the fooditem added to the cart
                try:
                    check_cart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if check_cart.quantity > 1:
                        # decrease the cart quantity
                        check_cart.quantity -= 1
                        check_cart.save()
                    else:
                        check_cart.delete()
                        check_cart.quantity=0
                    return JsonResponse({'status':'Success', 'cart_counter': get_cart_counter(request), 'qty': check_cart.quantity, 'cart_amount': get_cart_amount(request)})

                except:
                    return JsonResponse({'status':'Failed', 'message': 'You dont have item in this cart'})
            except:
                return JsonResponse({'status':'Failed', 'message': 'This food doesnot exist'})
        else:
            return JsonResponse({'status':'Failed', 'message': 'Invalid Response'})
    else:
        
        return JsonResponse({'status':'login_required', 'message': 'Please Login to continue'})


@login_required(login_url='login')
def cart(request):

    cart_items = Cart.objects.filter(user=request.user).order_by('fooditem__vendor','created_at')
    context = {
        'page_title': 'cart',

        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)


def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with', '').lower() == 'xmlhttprequest': # this line becz of django 5.0x
            try:
                # check if cart item exist
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status':'Success', 'message': 'Cart item Deleted','cart_counter': get_cart_counter(request),'cart_amount': get_cart_amount(request)})
            except:
                return JsonResponse({'status':'Failed', 'message': 'Cart item does not exist'})

        else:
            return JsonResponse({'status':'Failed', 'message': 'Invalid Response'})
        
        
def search(request):

    if not 'address' in request.GET:
        return redirect('marketplace')
    
    else:
        address = request.GET["address"]
        latitude = request.GET["lat"]
        longitude = request.GET["lng"]
        radius = request.GET["radius"]
        keyword = request.GET["keyword"]

        # get vendor's id that has the food item
        fetch_vendors_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)

        # the below q is used for complex query
        vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
        
        if latitude and longitude and radius:

            location_based = False

            if location_based:
                pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))
                print("Point Received: ",pnt)

                user_profile = UserProfile.objects.get(user=request.user)
                print("User Location from DB:", user_profile.location)


                vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True),
                user_profile__location__distance_lte=(pnt,D(km=radius))
                ).annotate(distance=Distance("user_profile__location",pnt)).order_by("distance")
                

                for v in vendors:
                    v.kms = round(v.distance.km, 1)

            vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True))
    
        vendor_count = vendors.count()
        context ={
            'page_title':'nearby-resturant',
            'vendors': vendors,
            'vendor_count': vendor_count,
            'source_location': address,
        }
        return render(request, 'marketplace/listings.html',context)


@login_required(login_url='login')
def checkout(request):

    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    
    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'phone': request.user.phone_number,

        'address':user_profile.address,
        'country':user_profile.country,
        'state':user_profile.state,
        'city':user_profile.city,
        'pin_code':user_profile.pincode,
    }
    form = OrderForm(initial=default_values)

    if cart_count <= 0:
        return redirect('marketplace')
    
    use_pay_pal = USE_PAY_PAL    
    context ={
        'page_title': f'checkout-{request.user.first_name}',
        'form': form,
        'cart_items': cart_items,
        'use_pay_pal':use_pay_pal,
    }
    return render(request, 'marketplace/checkout.html', context)