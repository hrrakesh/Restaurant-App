from django.contrib import admin
from .models import Category, FoodItem
from vendor.utils import generate_random_slug, get_unique_slug


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'vendor', 'updated_at')
    search_fields = ('category_name', 'vendor__vendor_name', )
    list_filter = ('category_name', 'vendor__vendor_name', )

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            base_slug = generate_random_slug()
            obj.slug = get_unique_slug(Category, base_slug)
        super().save_model(request, obj, form, change)


class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('food_title', 'category', 'vendor', 'price', 'is_available', 'updated_at')
    search_fields = ('food_title', 'category__category_name', 'price')
    list_filter = ('is_available', 'vendor__vendor_name', 'category__category_name')

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            base_slug = generate_random_slug()
            obj.slug = get_unique_slug(FoodItem, base_slug)
        super().save_model(request, obj, form, change)


admin.site.register(Category, CategoryAdmin)
admin.site.register(FoodItem, FoodItemAdmin)
