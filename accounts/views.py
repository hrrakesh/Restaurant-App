import datetime
from django.shortcuts import render, redirect
from orders.models import Order
from vendor.models import Vendor
from .models import User,UserProfile
from .forms import UserForm
from .utils import detect_user, send_verification_email, send_email_alert
from vendor.forms import VendorForm
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator


# Decorator to check if the user is logged in
def redirect_if_logged_in(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request,'Please logout to view that page😜')
            return redirect('my-account') 
        return view_func(request, *args, **kwargs)
    return wrapper


# Restrict Vendor from accessing Customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied

# Restrict Customer from accessings Vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied



@redirect_if_logged_in
def register_user(request):

    if request.method == 'POST': 
        
        form = UserForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.role = User.CUSTOMER
            user.set_password(password)
            user.save()

            # send verification message
            try:
                mail_subject = 'Please Verify your email -Customer-Account'
                email_template = 'accounts/email/account_verification_email.html'

                send_verification_email(request, user, mail_subject, email_template)
                
                messages.success(request, 'Mail sent for verfication')

            except Exception as e:

                messages.info(request,'Oops something went wrong!🤔')
                return redirect('login')

            messages.success(request, 'Your account has been successfully registered.😊')
            
            
            try:
                email_title = 'Account Created-Customer'
                email_template = 'accounts/email/alerts-email.html'
                message_body = """
                                Your customer account has been successfully created.
                                Welcome to Food-Online! We provide the best platform for food ordering.
                                Thank you for choosing Food-Online.😊❤️

                                """
                send_email_alert(request, user, email_title, email_template, message_body)
                return redirect('login')
            
            except Exception as e:
                pass
            
            return redirect('login')
        else:
            messages.warning(request, 'Some Credentials are wrong⚠️') 

    else:
        form = UserForm() 
    
    context = {
        'form': form,
        'page_title':'register-user',
    }
    return render(request, 'accounts/register-user.html',context)



from vendor.utils import generate_random_slug, get_unique_slug
@redirect_if_logged_in
def register_vendor(request):
    
    if request.method == 'POST':

        u_form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)

        if u_form.is_valid() and v_form.is_valid():
            password = u_form.cleaned_data['password']
            user = u_form.save(commit=False)
            user.set_password(password)
            user.role = User.VENDOR

            user.save()

            # VENDOR PART

            vendor = v_form.save(commit=False)
            vendor.user = user
            

            base_slug = generate_random_slug()
            slug = get_unique_slug(Vendor, base_slug)

            vendor.slug = slug
            
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            # send verification message
            try:
                
                mail_subject = 'Please Verify your email Vendor-Account'
                email_template = 'accounts/email/account_verification_email.html'
                
                send_verification_email(request, user, mail_subject, email_template)
                
                messages.success(request, 'Please Check your mail for verification')
                
            except Exception as e:
                
                messages.info(request,'Couldnt send the mail please contact Rakesh')
                return redirect('login')

            messages.success(request, 'Your account has been succesfully registered!❤️')
            
            try:
                email_title = 'Account Created-Vendor'
                email_template = 'accounts/email/alerts-email.html'
                message_body = """
                                Your Vendor Account is successfully Created
                                Welcome to Food-online, We provide best platform FoodMarketing 
                                and thanks for choosing @ Food-online

                                Note: Please Verify your Mail and wait for admin approval😊

                                """
                send_email_alert(request, user, email_title, email_template, message_body)
                return redirect('login')
            
            except Exception as e:
                pass

            return redirect('login') 
        else:
            messages.warning(request, 'Form is not valid! please try again⚠️')
            return redirect('login') 
    else:
        u_form = UserForm()
        v_form = VendorForm() # other than POST request

    context = {
        'u_form': u_form,
        'v_form': v_form,
        'page_title':'register-vendor',
    }

    return render(request,'accounts/register-vendor.html', context)



@redirect_if_logged_in
def forgot_password(request):

    if request.method == 'POST':
        email = request.POST['email']
        user = User.objects.get(email=email)

        if user is not None and user.is_active and not user.is_freeze:
            #send reset password email
            try:
                mail_subject = 'Reset-Password Link'
                email_template = 'accounts/email/reset_password_email.html'
                
                send_verification_email(request, user, mail_subject, email_template)
                
                messages.success(request, 'We have sent the link. Please check your mail.')
                return redirect('login')
            
            except Exception as e:
                messages.info(request,'Something went wrong please contact rakesh')
                return redirect('login')
        else:
            if not user.is_active:
                messages.warning(request, 'Please reverify your email.❤️')
                return redirect('re-activate')
            elif user.is_freeze:
                messages.warning(request, 'Youre Account is Suspended😰')
                return redirect('login')
            else:
                user = None  
                messages.warning(request, "We don't have an account associated with the provided email.🤔")
                return redirect('register-user') 
    else:   
        context = {'page_title':'forgot-password'} # other than POST request
    
    return render(request, 'accounts/forgot-password.html', context)

@redirect_if_logged_in
def reset_password_validate(request, uidb64, token):
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
        
    except(TypeError, OverflowError, User.DoesNotExist, ValueError):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Link validated🫡')
        return redirect('reset-password')
    else:
        messages.error(request, 'Invalid Link')
        return redirect('forgot-password')


@redirect_if_logged_in
def reset_password(request):

    if request.method == 'POST':
        password = request.POST['password'] 
        confirm_password = request.POST['confirm_password'] 
        
        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password Set Successfully')
            
            try:
                email_title = 'Your password is updated😊'
                email_template = 'accounts/email/alerts-email.html'
                message_body = """
                We have noticed that you updated your password.
                We hope you have verified this activity. If not, please report it immediately.
                Report: CustomerCare@food-online
                """
                send_email_alert(request, user, email_title, email_template, message_body)
                return redirect('login')
            
            except Exception as e:
                pass
            return redirect('login')
        else:
            messages.error(request, 'Password does not match')
            return redirect('reset-password') 
    
    else:
        try:
            uid_get = request.session.get('uid')

            if not uid_get:
                return redirect('forgot-password')  
            user = User.objects.get(pk=uid_get)

            context = {
                'page_title': 'reset-password',
                'user_email': user.email, 
            }
            return render(request, 'accounts/reset-password.html', context)
        
        except ObjectDoesNotExist:
            messages.error(request, 'Something went wrong')
            return redirect('forgot-password')


@redirect_if_logged_in
def re_activate(request): 
     
    if request.method == 'POST':
        email = request.POST.get('email')  
        try:
            user = User.objects.get(email=email) 
            if user is not None and not user.is_active and not user.is_freeze:
                
                try:
                    mail_subject = 'Please verify your email again.'
                    email_template = 'accounts/email/account_re_verification_email.html'
                    
                    send_verification_email(request, user, mail_subject, email_template)
                    
                    messages.success(request, 'We have sent the link. Please check your mail.')
                
                except Exception as e:
                        messages.error(request,'Something went wrong. Please contact Rakesh')
                        return redirect('login')
                
            else:
                if user.is_freeze:
                    messages.warning(request, 'Your account is suspended.😰')
                    return redirect('login')
                else:
                    messages.info(request, 'You have already verified. Please log in.😊')
                    return redirect('login')

        except User.DoesNotExist:
            user = None  
            messages.warning(request, "We don't have an account associated with the email provided")
            messages.warning(request, "Please create a new one.")
            print(e)
            return redirect('register-user')
    
    context = {'page_title': 're-activate'} 

    return render(request, 'accounts/re-activate.html', context)

@redirect_if_logged_in
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
        
    except(TypeError, OverflowError, User.DoesNotExist, ValueError):
        user = None

    from django.contrib.auth.tokens import default_token_generator
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations You have successfully verified..❤️')
        return redirect('my-account')

    else:
        messages.error(request, 'Invalid Activation Link')
        return redirect('my-account')

def login(request):

    context = {
        'page_title': 'login',
    }

    if request.user.is_authenticated:
        messages.warning(request, 'you are already logged in')
        return redirect('my-account')
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Successfully Logged in 😊')
            
            return redirect('my-account')
        else:
            messages.warning(request, 'Invalid Login Credentials😔')
            return redirect('login')

    return render(request, 'accounts/login.html', context)

def logout(request):
    
    auth.logout(request)
    messages.info(request, 'Successfully logged out❤️')
    return redirect('login')


@login_required(login_url='login')
def my_account(request):
    
    user = request.user
    redirect_url = detect_user(user)
    
    return redirect(redirect_url)


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def customer_dashboard(request):

    orders = Order.objects.filter(user=request.user, is_ordered=True)
    recent_orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')[:5]

    paginator = Paginator(recent_orders, 2) 

    page_number = request.GET.get('page')  # Get the current page number from the URL
    page_orders = paginator.get_page(page_number)  # Get the orders for the current page

    context ={
        'page_title':'customer-dasboard',
        'orders': page_orders,
        'orders_count': orders.count(),
    }
    return render(request, 'accounts/customer-dashboard.html',context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendor_dashboard(request):

    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')
    recent_orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')[:5]
    
    # total revenue 
    total_revenue = 0
    for per_order in orders:
        total_revenue += per_order.get_total_by_vendor()['grand_total']
    
    
    # current month revenue 
    current_month = datetime.datetime.now().month
    current_month_orders = orders.filter(vendors__in=[vendor.id], created_at__month = current_month)

    total_revenue_current_month = 0
    for per_order in current_month_orders:
        total_revenue_current_month += per_order.get_total_by_vendor()['grand_total']
    

    
    context ={
        'page_title':'vendor-dasboard',
        'orders': recent_orders,
        'orders_count': orders.count(),
        'total_revenue': total_revenue,
        'current_month_name' : datetime.datetime.now().strftime("%B"),
        'total_revenue_current_month':total_revenue_current_month,
        
    }
    return render(request, 'accounts/vendor-dashboard.html',context)