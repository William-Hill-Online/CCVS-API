import debug_toolbar

from .base import include
from .base import path
from .base import urlpatterns


urlpatterns = [
    path('__debug__/', include(debug_toolbar.urls)),
] + urlpatterns
