from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('brigada/', include('apps.brigada.urls')),
    path('modules/', include('apps.modules.urls')),
]

# This add the MEDIA_URL and MEDIA_ROOT to the urlpatterns when the app is in DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)