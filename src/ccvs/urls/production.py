from django.conf import settings
from django.conf.urls.static import static

from .base import urlpatterns

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
