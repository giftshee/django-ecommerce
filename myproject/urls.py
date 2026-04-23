"""
URL configuration for myproject project.
"""

from django.conf import settings
from django.conf.urls.static import static  # ✅ <--- ADD THIS LINE
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
    path('accounts/', include('accounts.urls')),
]

# ✅ Serve uploaded media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
