from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from . import views
from .views import (
    home_view,
    projects_by_category,
    ProjectCreateView, ProjectUpdateView, ProjectDeleteView,
    ProjectDetailView, ProjectListView, report_content,
    tag_autocomplete
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
    path('report/<str:content_type>/<int:object_id>/', report_content, name='report_content'),
    path('latest/', views.LatestProjectsView.as_view(), name='latest'),
    path('<int:project_id>/rate/', views.rate_project, name='rate_project'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('tag-autocomplete/', tag_autocomplete, name='tag-autocomplete'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)