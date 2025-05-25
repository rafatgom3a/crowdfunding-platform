# from django.http import HttpResponse
# def home(request):
#     return HttpResponse("Welcome to the homepage")

from django.shortcuts import render
from projects.models import Project, Category
from .models import FeaturedProject
from django.db.models import Avg, Q


def homepage(request):
    top_rated_projects = Project.objects.filter(is_running=True).annotate(avg_rating=Avg('ratings__value')).order_by('-avg_rating')[:5]
    latest_projects = Project.objects.all().order_by('-created_at')[:5]
    featured_projects = FeaturedProject.objects.select_related('project').order_by('-created_at')[:5]
    categories = Category.objects.all()
    query = request.GET.get('q')

    if query:
        search_results = Project.objects.filter(Q(title__icontains=query) | Q(tags__name__icontains=query)).distinct()
    else:
        search_results = None

    return render(request, 'core/home.html', {
        'top_rated_projects': top_rated_projects,
        'latest_projects': latest_projects,
        'featured_projects': [fp.project for fp in featured_projects],
        'categories': categories,
        'search_results': search_results,
        'query': query
    })
