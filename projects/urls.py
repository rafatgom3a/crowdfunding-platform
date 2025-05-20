from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.home_view, name='home'), # Assuming you have a home_view
    # ... other project URLs ...
]