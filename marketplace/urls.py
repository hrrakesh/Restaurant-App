from django.urls import path
from . import views


urlpatterns = [

    path('', views.marketplace, name='marketplace'),
    path('<slug:vendor_slug>/', views.vendor_details, name='vendor-details'),

    path('add-to-cart/<int:food_id>/', views.add_to_cart, name='add-to-cart'),
    path('decrease-cart/<int:food_id>/', views.decrease_cart, name='decrease-cart'),

    path('delete-cart/<int:cart_id>/', views.delete_cart, name='delete-cart')

]