from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from marketplace import views as Marketplace

urlpatterns = [

    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('', include('accounts.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('cart/', Marketplace.cart, name='cart'),
    path('checkout/', Marketplace.checkout, name='checkout'),
    path('orders/', include('orders.urls')),

    path('newsletter', views.newsletter, name='newsletter'),
    path('search/', Marketplace.search, name='search')


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
