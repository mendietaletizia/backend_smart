from django.urls import path
from . import views
from . import checkout_views

app_name = 'ventas_carrito'

urlpatterns = [
    path('carrito/', views.CarritoView.as_view(), name='carrito'),
    path('carrito/management/', views.CarritoManagementView.as_view(), name='carrito_management'),
    path('checkout/', checkout_views.CheckoutView.as_view(), name='checkout'),
]