from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point
from .utils import profile_choices

class UserManager(BaseUserManager):
    
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError("Email Required")
        if not username:
            raise ValueError("Username Required")
        
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, password=None):
        # Call the regular user creation method first
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,  
            password=password,
        )
        
        user.is_admin = True
        user.is_active = True  
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    VENDOR = 1
    CUSTOMER = 2

    ROLE_CHOICE = (
        (VENDOR, 'VENDOR'),
        (CUSTOMER, 'CUSTOMER'),
    )


    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=12, blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICE, blank=True, null=True)

    objects = UserManager()

    date_join = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)  

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)  
    is_freeze = models.BooleanField(default=False)  
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
    
    def get_role(self):
        if self.role == 1:
            return 'VENDOR'
        elif self.role == 2:
            return 'CUSTOMER'


class UserProfile(models.Model):
    
    use_choices = False
    
    COUNTRIES = profile_choices('c')
    INDIA_STATES = profile_choices('s')
    INDIA_CITIES_CHOICES = profile_choices('ci')

    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='users/profile_pictures', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='users/cover_photo', blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    
    if use_choices:
        country = models.CharField(max_length=20, choices=COUNTRIES, blank=True)  
        state = models.CharField(max_length=20, choices=INDIA_STATES, blank=True) 
        city = models.CharField(max_length=50, choices=INDIA_CITIES_CHOICES, blank=True)  
    else:
        country = models.CharField(max_length=20,  blank=True)  
        state = models.CharField(max_length=20, blank=True) 
        city = models.CharField(max_length=50,  blank=True)
    
    pincode = models.CharField(max_length=10, blank=True, null=True)
    latitude = models.CharField(blank=True, null=True)  
    longitude = models.CharField(blank=True, null=True)  
    location = gismodels.PointField(blank=True, null=True, srid=4326)  # Spatial reference identifier
    
    
    def __str__(self):
        return self.user.email
    
    save_s = True

    if save_s:
        def save(self, *args, **kwargs):

            if self.latitude and self.longitude:
                try:
                    self.location = Point(float(self.longitude), float(self.latitude))  
                except (TypeError, ValueError) as e:
                    raise ValueError(f"Invalid latitude or longitude: {e}")
            super(UserProfile, self).save(*args, **kwargs)
        

class NewsSub(models.Model):
    email = models.EmailField(max_length=25,unique=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email