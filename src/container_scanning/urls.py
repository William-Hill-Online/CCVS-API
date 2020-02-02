from django.urls import path

from .views import jobs, vendors

app_name = 'container_scanning'

urlpatterns = [
    path('vendors/', vendors.VendorsView.as_view(), name='vendor-list'),
    path('vendors/<uuid:vendor_id>/', vendors.VendorView.as_view(), name='vendor'),
    path('jobs/', jobs.JobsView.as_view(), name='jobs'),
    path('jobs/<uuid:job_id>/', jobs.JobView.as_view(), name='job'),
]
