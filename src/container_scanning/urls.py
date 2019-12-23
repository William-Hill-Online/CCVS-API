from django.urls import path

from .views import images
from .views import vendors

app_name = 'container_scanning'

urlpatterns = [
    path('vendors/', vendors.VendorsView.as_view(), name='vendor-list'),
    path('vendors/<uuid:vendor_id>/',
         vendors.VendorView.as_view(), name='vendor'),

    path('images/', images.ImagesView.as_view(), name='image-list'),
    path('images/<uuid:image_id>/', images.ImageView.as_view(), name='image'),

    path('images/<uuid:image_id>/vendor/<uuid:vendor_id>/',
         images.ImageVendorView.as_view(), name='image-vendor'),
    path('images/<uuid:image_id>/vendor/<uuid:vendor_id>/vuln/',
         images.ImageVendorVulnView.as_view(), name='image-vendor-vuln'),
]
