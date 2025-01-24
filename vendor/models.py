from django.db import models
from accounts.models import User, UserProfile
from .utils import send_notification,get_days,get_hours
from datetime import date,datetime

# Create your models here.

class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True,max_length=100, unique=True)
    top_rated = models.BooleanField(default=True)
    rest_status = models.BooleanField(default=False)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def check_rest_status(self):
        today_date = date.today()
        today = today_date.isoweekday()
        current_opening_hours_check = OpeningHours.objects.filter(vendor=self, day=today)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        is_open = None
        for i in current_opening_hours_check:
            start = str(datetime.strptime(i.from_hours, "%I:%M %p").time())
            end = str(datetime.strptime(i.to_hours, "%I:%M %p").time())
            
            if current_time > start and  current_time < end:
                is_open = True
                is_open = not(i.is_holiday) and is_open and self.rest_status
                break
            else:
                is_open = False
    
        return is_open
         

    def __str__(self):
        return self.vendor_name
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            # update
            orignal_before_update = Vendor.objects.get(pk=self.pk)
           
            if orignal_before_update.is_approved != self.is_approved: # checking with previous whether the status as changed or not
                if self.is_approved == True:
                    # send Congratualation notificaion
                    try:
                        
                        mail_subject = 'Your Restaurant License As been Approved Congratulation!'
                        email_path = 'accounts/email/notification-email.html'
                        message_body = """

                                    Your Restaurant Account License is Approved.  
                                    We have reviewed your documents and approved them. You can now list your items on our portal.  

                                    **FoodOnline**: Your one-stop solution for all food-related needs.  

                                    For any inquiries, contact: **Customer-care@foodonline**  

                                    With regards,  
                                    Admin [FoodOnline]  

                                    [Note: Please do not reply to this auto-generated email.]  

                                    """
                        context = {
                            'user': self.user,
                            'is_approved': self.is_approved,
                            'message_body': message_body,
                        }
                        # send_notification(mail_subject, email_path, context)

                    except Exception as e:
                        print(e)
                    
                else:
                    #send Rejected Notification
                    try:
                        
                        mail_subject = 'Your Restaurant License As been Rejected'
                        email_path = 'accounts/email/notification-email.html'
                        
                        message_body = """

                                    As we see, there is an issue with the Restaurant license.
                                    For more information, please contact the admin on our portal.
                                    FoodOnline: Your one-stop solution for all food-related needs.
                                    For any inquiries, contact: admin-care@foodonline

                                    with regard,
                                    Food-online

                                    [Note: Please - dont reply to this email here please contact to the email provided]
                                    
                                    """
                        
                        context = {
                            'user': self.user,
                            'is_approved': self.is_approved,
                            'message_body': message_body,
                        }
                        send_notification(mail_subject, email_path, context)
                    except Exception as e:
                        print(e)

        return super(Vendor, self).save(*args, **kwargs)

class OpeningHours(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=get_days())
    from_hours = models.CharField(choices=get_hours(), max_length=20, blank=True)
    to_hours = models.CharField(choices=get_hours(), max_length=20, blank=True)
    is_holiday = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'OpeningHours'
        verbose_name_plural = 'Opening Hours'
        ordering = ('day', '-from_hours')
        unique_together = ('vendor','day', 'from_hours', 'to_hours')
    
    def __str__(self):
        return self.get_day_display()