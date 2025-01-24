from django.urls import include, path
from . import views
from accounts import views as AccountViews

urlpatterns = [

    path('', AccountViews.customer_dashboard, name='customer'),
    path('customer-profile/', views.customer_profile, name='customer-profile'),
    path('my-orders/', views.my_orders, name='my-orders'),
    path('order-details/<str:order_number>/', views.order_details, name='order-details')

]
