from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.ProductoListView.as_view(), name='list_products'),
    path('admin/', views.ProductoAdminView.as_view(), name='admin_products'),
    path('upload-image/', views.UploadImageView.as_view(), name='upload_image'),
]

