
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

def send_notification(mail_subject, email_path, context):
    
    from_email = settings.DEFAULT_NOTIFICATION_FROM_EMAIL
    
    to_email = context['user'].email
    mail_subject = mail_subject
    email_path = email_path
    
    
    message = render_to_string(email_path,context)

    
    mail = EmailMessage(mail_subject, message, from_email,to=[to_email])
    mail.send()



import random
import string


def generate_random_slug(k=6):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choices(letters_and_digits, k=k))  # 6 characters only

# Function to check if the slug is unique
def get_unique_slug(model, base_slug):
    slug = base_slug
    while model.objects.filter(slug=slug).exists():  # Check if slug exists
        slug = generate_random_slug()  # Generate a new one if exists
    return slug

def get_days():
    DAYS = [
        (1, "Monday"),
        (2, "Tuesday"),
        (3, "Wednesday"),
        (4, "Thursday"),
        (5, "Friday"),
        (6, "Saturday"),
        (7, "Sunday"),
    ]

    return DAYS

from datetime import time
import time as t
def get_hours():
    hours = []
    for h in range(0,24):
        for m in (0,30):
            each_hour = time(h,m).strftime('%I:%M %p')
            hours.append((each_hour, each_hour)) # actually it is taking 0 and converting that to 12
    return hours


