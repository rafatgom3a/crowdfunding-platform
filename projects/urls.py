from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from accounts import views
from .views import (
    home_view,
    projects_by_category,
    ProjectCreateView, ProjectUpdateView, ProjectDeleteView,
    ProjectDetailView, ProjectListView, report_content
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
    path('report/<str:content_type>/<int:object_id>/', report_content, name='report_content')
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)