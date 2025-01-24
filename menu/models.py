from django.db import models
from vendor.models import Vendor


class Category(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=40)
    slug = models.SlugField(blank=True, max_length=100, unique=True)  # this is the URL for the category name
    description = models.TextField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        # Ensure category_name is unique within each vendor
        constraints = [
            models.UniqueConstraint(fields=['vendor', 'category_name'], name='unique_vendor_category')
        ]

    def __str__(self):
        return self.category_name

    def save(self, *args, **kwargs):
        
        if not self.pk:  
            existing_category = Category.objects.filter(category_name=self.category_name).exclude(vendor=self.vendor).first()
            if existing_category:
                # Append the first 3 letters of the vendor's name to the category_name
                self.category_name = f"{self.category_name}-{self.vendor.vendor_name}"
        
        super().save(*args, **kwargs) 
    

class FoodItem(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='fooditems')
    food_title = models.CharField(max_length=20)
    slug = models.SlugField(blank=True,max_length=100)
    description = models.TextField(max_length=250, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='food-images')
    is_available = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.food_title