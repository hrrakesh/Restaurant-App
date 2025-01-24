from django.http import  JsonResponse
from django.shortcuts import render,get_object_or_404,redirect
from orders.models import Order, OrderFood
from .forms import VendorForm, OpeningHoursForm
from accounts.forms import UserProfileForm
from menu.forms import CategoryForm, FoodItemForm
from accounts.models import UserProfile
from .models import OpeningHours, Vendor
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor
from menu.models import Category, FoodItem
from django.db import IntegrityError
from django.core.paginator import Paginator


def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendor_profile(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)

        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Profile Updated❤️')
            return redirect('vendor-profile')
        else:
            pass # form not vaild
            
        
    else:
        # passing instance because to load the existing instance 
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)
    
    rest_status = vendor.rest_status
    print(rest_status)
    context = {
        'page_title': 'vendor-profile',
        'profile_form': profile_form,
        'vendor_form' : vendor_form,
        'profile': profile,
        'vendor': vendor,
        'current_rest_status': rest_status,
    }
    return render(request, 'vendor/vendor-profile.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('category_name')

    context = {
        'page_title': 'menu-builder',
        'vendor': vendor,
        'categories': categories,
    }
    return render(request, 'vendor/menu-builder.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def food_items_by_category(request, pk=None):
    
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    

    context = {
        'page_title': 'food-category',
        'fooditems': fooditems,
        'category': category,
    }
    return render(request, 'vendor/food-items-by-category.html', context)


from vendor.utils import generate_random_slug, get_unique_slug
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            vendor = get_vendor(request)

            try:
                # Check if the category already exists for the given vendor
                existing_category = Category.objects.filter(category_name=category_name, vendor=vendor).first()
                if existing_category:
                    messages.error(request, f'Error: Category "{category_name}" already exists for this vendor.')
                    return redirect('add-category')

                # Check if the category exists for another vendor
                category_for_other_vendor = Category.objects.filter(category_name=category_name).exclude(vendor=vendor).first()
                if category_for_other_vendor:
                    # Append the vendor's name to the category if it exists for another vendor
                    category_name = f"{category_name}-{vendor.vendor_name}"

                # Generate a unique slug
                base_slug = generate_random_slug()
                slug = get_unique_slug(Category, base_slug)

                # Create and save the category
                category = form.save(commit=False)
                category.vendor = vendor
                category.category_name = category_name  # Save the modified category name
                category.slug = slug
                category.save()

                messages.success(request, 'Category added successfully')
                return redirect('menu-builder')

            except Exception as e:
                messages.error(request, 'We can see that the details already exist. or edit the details')
                return redirect('add-category')
        else:
            messages.error(request, 'Error: Invalid data provided.')
    else:
        form = CategoryForm()

    context = {
        'page_title': 'add-category',
        'form': form,
    }
    return render(request, 'vendor/category/add-category.html', context)



@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            vendor = get_vendor(request)

            # Check if a category with the same name exists under a different vendor
            existing_category = Category.objects.filter(category_name=category_name).exclude(vendor=vendor).first()
            if existing_category:
               
                category_name = f"{category_name}-{vendor.vendor_name}"

            base_slug = generate_random_slug()
            slug = get_unique_slug(Category, base_slug)

            # Check if a category with the same slug already exists for the vendor
            if Category.objects.filter(slug=slug, vendor=vendor).exists():
                messages.error(request, f'A category already exists.')
                return redirect('menu-builder')

            try:
                # Check if the category name has changed
                if category_name != category.category_name:
                    # Append vendor name only if name has changed
                    import random

                    category_name = f"{category_name}-{random.randint(100, 999)}"

                # Save the updated category
                category = form.save(commit=False)
                category.vendor = vendor
                category.category_name = category_name  # Update the category name if changed
                category.slug = slug
                category.save()
                
                messages.success(request, 'Category updated successfully.')
                return redirect('menu-builder')

            except IntegrityError:
                messages.error(request, f'Error: Category with this name already exists.')
        else:
            messages.error(request, f'Error: Invalid data provided.')
    else:
        form = CategoryForm(instance=category)

    context = {
        'page_title': 'edit-category',
        'form': form,
        'category': category,
    }

    return render(request, 'vendor/category/edit-category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    try:
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        messages.success(request, 'Category deleted successfully')
        return redirect('menu-builder')
    except Exception as e:
        messages.info(request, 'Something went wrong. Please refresh.')
        return redirect('menu-builder')
    
# food crud

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):

    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']

            base_slug = generate_random_slug()
            slug = get_unique_slug(FoodItem, base_slug)

            vendor = get_vendor(request)

            
            if FoodItem.objects.filter(slug=slug, vendor=vendor).exists():
                messages.error(request, f'A Food-title with the name "{food_title}" already exists.')
            else:
                # Create the category
                food = form.save(commit=False)
                food.vendor = vendor
                food.slug = slug
                food.save()
                messages.success(request, 'Food-item added successfully')
                return redirect('food-items-by-category', food.category.id)
        else:
            messages.error(request, f'Error: Food-title already exists.')
    else:
        form = FoodItemForm()
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    
    context = {
        'form': form,
        'page_title': 'add-food',
    }
    return render(request, 'vendor/food/add-food.html', context) 


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    
    food = get_object_or_404(FoodItem, pk=pk)
    
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']

            base_slug = generate_random_slug()
            slug = get_unique_slug(FoodItem, base_slug)

            vendor = get_vendor(request)

            try:
                # Check if the name has changed
                if food_title != FoodItem.food_title:
                    # Check if a food with the same slug already exists for the vendor
                    if Category.objects.filter(slug=slug, vendor=vendor).exists():
                        messages.info(request, f'food name already exists.')
                        return redirect('food-items-by-category', food.category.id)

                
                food = form.save(commit=False)
                food.vendor = vendor
                food.slug = slug
                food.save()
                messages.success(request, 'Food-item updated successfully.')
                return redirect('food-items-by-category', food.category.id)

            except IntegrityError:
                messages.error(request, f'Error: Food-item with this name already exists.')
        else:
            messages.error(request, f'Error: Invalid data provided.')
    else:
        form = FoodItemForm(instance=food)
        # modifiy the form
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
        

    context = {
        'page_title': 'edit-food',
        'form': form,
        'food':food,
        
    }
    return render(request, 'vendor/food/edit-food.html',context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_food(request, pk=None):
    try:
        food = get_object_or_404(FoodItem, pk=pk)
        food.delete()
        messages.success(request, 'Food-item deleted successfully')
        return redirect('food-items-by-category', food.category.id)
    except Exception as e:
        messages.error(request, 'Something went wrong, Please Refresh')
        #messages.success(request, e)
        return redirect('menu-builder')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def opening_hours(request):

    opening_hours = OpeningHours.objects.filter(vendor=get_vendor(request))
    
    opening_hours_form = OpeningHoursForm()
    context = {
        'page_title': 'opening-hours',
        'opening_hours':opening_hours,
        'form': opening_hours_form,
    }
    return render(request,'vendor/opening-hours.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def opening_hours_add(request):
    if request.user.is_authenticated:
        # Check if the request is an AJAX POST request
        if request.headers.get('x-requested-with', '').lower() == 'xmlhttprequest' and request.method == 'POST':
            day = request.POST.get('day')
            from_hours = request.POST.get('from_hours')
            to_hours = request.POST.get('to_hours')
            is_holiday = request.POST.get('is_holiday')
            
            # Convert 'is_holiday' from string to boolean
            is_holiday = True if is_holiday.lower() == 'true' else False
            
            # Fetch vendor for the current request
            vendor = get_vendor(request)
            print(day,from_hours,to_hours,is_holiday,vendor)
           
            
            # Check if an identical entry already exists
            existing_entry = OpeningHours.objects.filter(
                vendor=vendor,
                day=day,
                from_hours=from_hours,
                to_hours=to_hours,
                # is_holiday__in=[True, False]
            ).exists()
            
            if existing_entry:
                response = {
                    'status': 'Exist',
                    'message': 'Details Exist!🤔',
                }
                return JsonResponse(response)
            
            # Count entries for the same day for this vendor
            days_count = OpeningHours.objects.filter(day=day, vendor=vendor).count()
            
            # Check if the limit of 5 entries is reached
            if days_count >= 5:
                response = {
                    'status': 'fail',
                    'message': 'Limit exceeded: Maximum of 5 entries allowed for the same day!😔',
                }
                return JsonResponse(response)
            
            try:
                # Create a new entry
                hours = OpeningHours.objects.create(
                    vendor=vendor,
                    day=day,
                    from_hours=from_hours,
                    to_hours=to_hours,
                    is_holiday=is_holiday
                )
                
                if hours:
                    # Fetch the newly created entry
                    day_obj = OpeningHours.objects.get(id=hours.id)
                    
                    # Construct the success response
                    if day_obj.is_holiday:
                        response = {
                            'status': 'success',
                            'id': hours.id,
                            'day': day_obj.get_day_display(),
                            'is_holiday': 'True',
                            'from_hours': from_hours,
                            'to_hours': to_hours,
                            'message': 'Added Successfully!',
                        }
                    else:
                        response = {
                            'status': 'success',
                            'id': hours.id,
                            'day': day_obj.get_day_display(),
                            'from_hours': hours.from_hours,
                            'to_hours': hours.to_hours,
                            'message': 'Added Successfully!',
                        }
                    return JsonResponse(response)
            except IntegrityError:
                response = {
                    'status': 'failed',
                    'message': 'Failed to add the element.',
                }
                return JsonResponse(response)
    else:
        messages.info(request, "Request Invalid")
    

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def opening_hours_delete(request, pk=None):
    if request.user.is_authenticated:
    # Check if the request is an AJAX POST request
        if request.headers.get('x-requested-with', '').lower() == 'xmlhttprequest' and request.method == 'GET':
            hour = get_object_or_404(OpeningHours, pk=pk)
            hour.delete()
            response = {
                'status':'success',
                'id':pk,
            }
            return JsonResponse(response)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def order_details(request, order_number):

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        order_food = OrderFood.objects.filter(order=order, fooditem__vendor=get_vendor(request)).order_by('fooditem__food_title')
        print(order_food)
    except Exception as e:
        print("went wrong with : ",e)
        order = None
    
    context = {
        'page_title': 'order-details-' + order_number,
        'order':order,
        'ordered_food': order_food,
        'subtotal': order.get_total_by_vendor()['subtotal'],
        'tax_dict': order.get_total_by_vendor()['tax_dict'],
        'grand_total':order.get_total_by_vendor()['grand_total'],
    }
    return render(request, 'vendor/order-details.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def my_orders(request):
    vendor = Vendor.objects.get(user=request.user)

    orders = Order.objects.filter( vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')

    paginator = Paginator(orders, 5) 

    page_number = request.GET.get('page')  # Get the current page number from the URL
    page_orders = paginator.get_page(page_number)  # Get the orders for the current page

    context  ={
        'page_title': 'my-orders',
        'orders': page_orders,
        'orders_count': orders.count()
    }
    return render(request, 'vendor/my-orders.html', context)