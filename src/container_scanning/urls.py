from django.urls import path

from .views import analyses, vendors

app_name = 'container_scanning'

urlpatterns = [
    path('vendors/', vendors.VendorsView.as_view(), name='vendor-list'),
    path('vendors/<uuid:vendor_id>/', vendors.VendorView.as_view(), name='vendor'),
    path('analysis/', analyses.AnalysisView.as_view(), name='analysis'),
    path('analysis/<uuid:analysis_id>/',
         analyses.AnalysisIdView.as_view(), name='analysis-id'),
]
