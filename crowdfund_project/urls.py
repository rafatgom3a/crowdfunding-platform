from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.core.mail import send_mail


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls', namespace='accounts')),  # Change namespace to 'accounts'
    path('users/', include('users.urls', namespace='users')),
    path('', include('projects.urls', namespace='projects')),
    # Add other app URLs here
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
