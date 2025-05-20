from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.core.mail import send_mail


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls', namespace='users')),
    path('users/', include('users.urls', namespace='users')),
    path('', include('projects.urls', namespace='projects')),
   # path('', include('projects.urls', namespace='projects')), # Assuming you have a projects app for homepage
    # Add other app URLs here
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # If using STATIC_ROOT for dev
