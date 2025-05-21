from django.urls import path
from .views import (
    home_view,
    ProjectCreateView, ProjectUpdateView, ProjectDeleteView,
    ProjectDetailView, ProjectListView,
)

app_name = 'projects'  

urlpatterns = [
    path('', home_view, name='home'),
    path('list/', ProjectListView.as_view(), name='list'),  
    path('create/', ProjectCreateView.as_view(), name='create'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', ProjectUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', ProjectDeleteView.as_view(), name='delete'),
]
