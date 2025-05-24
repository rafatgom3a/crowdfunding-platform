from django.urls import path
from . import views

app_name = 'donations'
urlpatterns = [
    path('project/<int:project_id>/donate/', views.donate_to_project, name='donate'),
    path('donation', views.donation_success, name='donation_success'),
]