
from django.shortcuts import redirect, render
from vendor.models import Vendor
from accounts.models import NewsSub
from django.contrib import messages
from accounts.utils import send_new_news_letter
from accounts.models import UserProfile
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from .utils import get_or_set_current_location

def home(request):
    
    location_based = False

    lng, lat =  get_or_set_current_location(request)
    user = str(request.user)
    if user != 'AnonymousUser' and location_based and  lng is not None and lat is not None:
        
        pnt = GEOSGeometry('POINT(%s %s)' % (lng, lat))
        user_profile = UserProfile.objects.get(user=request.user)

        print('-'*10)
        print("Point Received: ",pnt)
        print("User Location from DB:", user_profile.location)
        print('-'*10)

        vendors = Vendor.objects.filter(user_profile__location__distance_lte=(pnt,D(km=100))
        ).annotate(distance=Distance("user_profile__location",pnt)).order_by("distance")
        
        for v in vendors:
            v.kms = round(v.distance.km, 1)
   
    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    
    context = {
        'page_title':'home',
        'vendors': vendors,
        'location_based': location_based,
    }
    return render(request,"home.html",context)



# Newsletter Subscription View
def newsletter(request):
    email = None
    is_success = False
    exist = False
    
    if request.method == "POST":
        email = request.POST.get('email')
        if email:
           
            # Check if email already exists in the database
            present_email = NewsSub.objects.filter(email=email)
            if present_email.exists():
                exist=True
                context = {
                    'is_success': is_success,
                    'email': email,
                    'exist': exist,
                 }
                
            else:
                is_success = True
                # Save the email to the database
                NewsSub.objects.create(email=email)
                

                try:
                    # Send confirmation email
                    mail_subject = 'New Email Registered for Newsletter'
                    email_template = 'accounts/email/news-sub.html'
                    message_body = f"Hi Rakesh, you have a new email: {email}"
                    send_new_news_letter(mail_subject, email_template, message_body)
                    return redirect('home')

                except Exception as e:
                    messages.success(request, 'You have successfully subscribed to the newsletter.❤️')
                    is_success = True
                    
                    return redirect('home')
    
    context = {
        'is_success': is_success,
        'email': email,
        'exist': exist,
    }
        

   
    return render(request, 'includes/newsletter_form.html', context)