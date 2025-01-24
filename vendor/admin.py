from django.contrib import admin
from .models import Vendor, OpeningHours
from django.utils.html import format_html
from vendor.utils import generate_random_slug, get_unique_slug

class VendorAdmin(admin.ModelAdmin):
    list_display = ('user', 'vendor_name', 'vendor_license_image', 'top_rated', 'rest_status','is_approved', 'created_at')
    list_display_links = ('user', 'vendor_name', 'vendor_license_image')
    list_editable = ('is_approved','top_rated','rest_status')

    def vendor_license_image(self, obj):
        if obj.vendor_license:  
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" width="50" height="50" style="border-radius: 5px;"/></a>',
                obj.vendor_license.url,  # Full-sized image URL
                obj.vendor_license.url   # Thumbnail image URL
            )
        return "No Image"
    vendor_license_image.short_description = "Vendor License" 

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            base_slug = generate_random_slug(k=10)
            obj.slug = get_unique_slug(Vendor, base_slug)
        super().save_model(request, obj, form, change)

class OpeningHoursAdmin(admin.ModelAdmin):
    list_display = ('vendor','day','from_hours', 'to_hours','is_holiday')
    list_editable = ('is_holiday',)

admin.site.register(Vendor, VendorAdmin)
admin.site.register(OpeningHours,OpeningHoursAdmin)