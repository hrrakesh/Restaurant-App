from django.urls import path
from . import views
from accounts import views as AccountViews

urlpatterns = [
        
        path('', AccountViews.vendor_dashboard, name='vendor' ),
        path('vendor-profile/',views.vendor_profile, name='vendor-profile'),
        path('menu-builder/', views.menu_builder, name='menu-builder'),
        path('menu-builder/category/<int:pk>/', views.food_items_by_category, name='food-items-by-category'),
        
        # category CRUD
        path('menu-builder/category/add/', views.add_category, name='add-category'),
        path('menu-builder/category/edit/<int:pk>/', views.edit_category, name='edit-category'),
        path('menu-builder/category/delete/<int:pk>/', views.delete_category, name='delete-category'),

        # FOOD ITEM CRUD
        path('menu-builder/food/add/', views.add_food, name='add-food'),
        path('menu-builder/food/edit/<int:pk>/', views.edit_food, name='edit-food'),
        path('menu-builder/food/delete/<int:pk>/', views.delete_food, name='delete-food'),

        # opening hours
        path('opening-hours/',views.opening_hours, name='opening-hours'),
        path('opening-hours/add/',views.opening_hours_add, name='opening-hours-add'),
        path('opening-hours/delete/<int:pk>/',views.opening_hours_delete, name='opening-hours-delete'),

        path('order-details/<str:order_number>/', views.order_details, name='vendor-order-details'),
        path('my-orders/', views.my_orders, name='vendor-my-orders'),
]