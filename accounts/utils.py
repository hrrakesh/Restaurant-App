from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.conf import settings

def detect_user(user):
    if user.role == 1:
        redirect_url = 'vendor-dashboard'
        return redirect_url
    elif user.role == 2:
        redirect_url = 'customer-dashboard'
        return redirect_url
    elif user.role == None and user.is_superadmin:
        redirect_url = '/admin'
        return redirect_url

def send_verification_email(request, user, mail_subject, email_template):
    
    from_email = settings.DEFAULT_FROM_EMAIL
    
    current_site = get_current_site(request)
    
    mail_subject = mail_subject
    email_path = email_template
    
    message = render_to_string(email_path, {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),  # Generate token for the user
    })

    to_email = user.email
    mail = EmailMessage(mail_subject, message, from_email,to=[to_email])
    mail.content_subtype = "html"

    mail.send()

def send_email_alert(request, user, mail_subject, email_template, message_body):
    
    from_email = settings.DEFAULT_ALERT_FROM_EMAIL
    
    mail_subject = mail_subject
    email_path = email_template
    message_body = message_body
    
    message = render_to_string(email_path, {
        'user': user,
        'message_body': message_body
    })

    to_email = user.email
    mail = EmailMessage(mail_subject, message, from_email,to=[to_email])
    mail.content_subtype = "html"

    mail.send()

def send_new_news_letter( mail_subject, email_template, message_body):
    print("from utils")
    from_email = settings.DEFAULT_NOTIFICATION_FROM_EMAIL_NEWS_ALERT 
    
    mail_subject = mail_subject
    email_path = email_template
    message_body = message_body
    
    message = render_to_string(email_path, {
        
        'message_body': message_body,
    })

    to_email = 'mandyarakesh23@gmail.com'
    mail = EmailMessage(mail_subject, message, from_email,to=[to_email])
    mail.content_subtype = "html"

    mail.send()


def send_notification(mail_subject, mail_template, context):
    from_email = settings.DEFAULT_NOTIFICATION_ORDER_CONFIRMATION
    message = render_to_string(mail_template, context)
    to_email = context['to_email']
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.content_subtype = "html"
    mail.send()



# End of email sending..

def profile_choices(code=None):

    if code == 'c':
        COUNTRIES = [
            ('India', 'India'),
        ]
        return COUNTRIES
    
    elif code == 's':
        INDIA_STATES = [
            ('Andhra Pradesh', 'Andhra Pradesh'),
            ('Assam', 'Assam'),
            ('Bihar', 'Bihar'),
            ('Chhattisgarh', 'Chhattisgarh'),
            ('Delhi', 'Delhi'),
            ('Goa', 'Goa'),
            ('Gujarat', 'Gujarat'),
            ('Haryana', 'Haryana'),
            ('Himachal Pradesh', 'Himachal Pradesh'),
            ('Jharkhand', 'Jharkhand'),
            ('Karnataka', 'Karnataka'),
            ('Kerala', 'Kerala'),
            ('Madhya Pradesh', 'Madhya Pradesh'),
            ('Maharashtra', 'Maharashtra'),
            ('Manipur', 'Manipur'),
            ('Meghalaya', 'Meghalaya'),
            ('Mizoram', 'Mizoram'),
            ('Nagaland', 'Nagaland'),
            ('Odisha', 'Odisha'),
            ('Punjab', 'Punjab'),
            ('Rajasthan', 'Rajasthan'),
            ('Sikkim', 'Sikkim'),
            ('Tamil Nadu', 'Tamil Nadu'),
            ('Telangana', 'Telangana'),
            ('Tripura', 'Tripura'),
            ('Uttar Pradesh', 'Uttar Pradesh'),
            ('Uttarakhand', 'Uttarakhand'),
            ('West Bengal', 'West Bengal'),
            ('others', 'others')
        ]
        return INDIA_STATES

    elif code == 'ci':
        INDIA_CITIES_CHOICES = [
            ('Visakhapatnam', 'Visakhapatnam'),
            ('Vijayawada', 'Vijayawada'),
            ('Tirupati', 'Tirupati'),
            ('Guwahati', 'Guwahati'),
            ('Dibrugarh', 'Dibrugarh'),
            ('Silchar', 'Silchar'),
            ('Patna', 'Patna'),
            ('Gaya', 'Gaya'),
            ('Bhagalpur', 'Bhagalpur'),
            ('Raipur', 'Raipur'),
            ('Bilaspur', 'Bilaspur'),
            ('Durg', 'Durg'),
            ('New Delhi', 'New Delhi'),
            ('Dwarka', 'Dwarka'),
            ('Saket', 'Saket'),
            ('Panaji', 'Panaji'),
            ('Margao', 'Margao'),
            ('Vasco da Gama', 'Vasco da Gama'),
            ('Ahmedabad', 'Ahmedabad'),
            ('Surat', 'Surat'),
            ('Vadodara', 'Vadodara'),
            ('Gurgaon', 'Gurgaon'),
            ('Faridabad', 'Faridabad'),
            ('Panchkula', 'Panchkula'),
            ('Shimla', 'Shimla'),
            ('Manali', 'Manali'),
            ('Dharamshala', 'Dharamshala'),
            ('Ranchi', 'Ranchi'),
            ('Jamshedpur', 'Jamshedpur'),
            ('Dhanbad', 'Dhanbad'),
            ('Bengaluru', 'Bengaluru'),
            ('Mysuru', 'Mysuru'),
            ('Mangaluru', 'Mangaluru'),
            ('Kochi', 'Kochi'),
            ('Thiruvananthapuram', 'Thiruvananthapuram'),
            ('Kozhikode', 'Kozhikode'),
            ('Bhopal', 'Bhopal'),
            ('Indore', 'Indore'),
            ('Gwalior', 'Gwalior'),
            ('Mumbai', 'Mumbai'),
            ('Pune', 'Pune'),
            ('Nagpur', 'Nagpur'),
            ('Imphal', 'Imphal'),
            ('Churachandpur', 'Churachandpur'),
            ('Ukhrul', 'Ukhrul'),
            ('Shillong', 'Shillong'),
            ('Cherrapunji', 'Cherrapunji'),
            ('Tura', 'Tura'),
            ('Aizawl', 'Aizawl'),
            ('Lunglei', 'Lunglei'),
            ('Champhai', 'Champhai'),
            ('Kohima', 'Kohima'),
            ('Dimapur', 'Dimapur'),
            ('Mokokchung', 'Mokokchung'),
            ('Bhubaneswar', 'Bhubaneswar'),
            ('Cuttack', 'Cuttack'),
            ('Rourkela', 'Rourkela'),
            ('Amritsar', 'Amritsar'),
            ('Chandigarh', 'Chandigarh'),
            ('Ludhiana', 'Ludhiana'),
            ('Jaipur', 'Jaipur'),
            ('Udaipur', 'Udaipur'),
            ('Jodhpur', 'Jodhpur'),
            ('Gangtok', 'Gangtok'),
            ('Pelling', 'Pelling'),
            ('Mangan', 'Mangan'),
            ('Chennai', 'Chennai'),
            ('Coimbatore', 'Coimbatore'),
            ('Madurai', 'Madurai'),
            ('Hyderabad', 'Hyderabad'),
            ('Warangal', 'Warangal'),
            ('Khammam', 'Khammam'),
            ('Agartala', 'Agartala'),
            ('Udaipur', 'Udaipur'),
            ('Ambassa', 'Ambassa'),
            ('Lucknow', 'Lucknow'),
            ('Kanpur', 'Kanpur'),
            ('Allahabad', 'Allahabad'),
            ('Mangalore', 'Mangalore'),
            ('Hassan', 'Hassan'),
            ('Chikmagalur', 'Chikmagalur'),
            ('Kolkata', 'Kolkata'),
            ('Howrah', 'Howrah'),
            ('Siliguri', 'Siliguri'),
            ('Lucknow', 'Lucknow'),
            ('Agra', 'Agra'),
            ('Kanpur', 'Kanpur'),
            ('Chandigarh', 'Chandigarh'),
            ('Faridabad', 'Faridabad'),
            ('Mohali', 'Mohali'),
            ('others', 'others')  
        ]

        return INDIA_CITIES_CHOICES
