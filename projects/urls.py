from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from . import views
from .views import (
    home_view,
    projects_by_category,
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
    path('category/<int:category_id>/', projects_by_category, name='projects_by_category'),
    path('latest/', views.LatestProjectsView.as_view(), name='latest'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)