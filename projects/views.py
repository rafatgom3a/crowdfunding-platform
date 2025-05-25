# from django.shortcuts import render
# from django.http import HttpResponse

# def home_view(request):
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from comments.forms import CommentForm
from .forms import ProjectForm, ProjectImageFormSet
from .models import Project, ProjectImage
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
# For now, let's return a simple HttpResponse
# Later, you'll render a template here
# return render(request, 'projects/home.html', {'title': 'Homepage'})
# Or, for a very basic test:
# return HttpResponse("<h1>Welcome to the Crowdfunding Platform Home!</h1>")
# Create your views here.


from decimal import Decimal
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from categories.models import Category
from django.db.models import Avg
from django.db.models import Q




def home_view(request):
    query = request.GET.get('q')
    if query:
        search_results = Project.objects.filter(
            Q(title__icontains=query) |
            Q(tags__name__icontains=query)  # If you're using taggit or related tag model
        ).distinct()
    else:
        search_results = None

    top_rated_projects = Project.objects.filter(is_active=True)\
    .annotate(avg_rating=Avg('ratings__value'))\
    .order_by('-avg_rating')[:5]

    latest_projects = Project.objects.filter(is_active=True).order_by('-start_time')[:5]
    featured_projects = Project.objects.filter(is_active=True, featuredproject__isnull=False).order_by('-start_time')[:5]
    categories = Category.objects.all()
    context = {
        'title': 'Homepage',
        'search_results': search_results,
        'query': query,
        'top_rated_projects': top_rated_projects,
        'latest_projects': latest_projects,
        'featured_projects': featured_projects,
        'categories': categories,
    }
    return render(request, 'projects/home.html', context)

from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from .models import Project, ProjectImage
from .forms import ProjectForm, ProjectImageFormSet
from comments.forms import CommentForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Project, ProjectImage, Rating
from .forms import ProjectForm, ProjectImageFormSet, RatingForm


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'category',
                  'tags', 'target_amount', 'end_time']


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"
    success_url = reverse_lazy("projects:list")

    # def form_valid(self, form):
    #     # Assign the logged-in user before saving the form
    #     form.instance.created_by = self.request.user
    #     return super().form_valid(form)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        images = self.request.FILES.getlist('images')
        for image_file in images:
            ProjectImage.objects.create(project=self.object, image=image_file)
        return response


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"
    success_url = reverse_lazy("projects:list")

    def form_valid(self, form):
        response = super().form_valid(form)

        # Delete selected images
        image_ids_to_delete = self.request.POST.getlist('delete_images')
        ProjectImage.objects.filter(
            id__in=image_ids_to_delete, project=self.object).delete()

        # Upload new images
        images = self.request.FILES.getlist('images')
        for image_file in images:
            ProjectImage.objects.create(project=self.object, image=image_file)

        self.object.check_cancellation()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['existing_images'] = self.object.project_images.all()
        return context


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = "projects/project_confirm_delete.html"
    success_url = reverse_lazy("projects:list")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if request.user != self.object.created_by and not request.user.is_superuser:
            return render(request, "projects/delete_restricted.html", {
                "message": "You are not allowed to delete this project."
            })

        if request.user == self.object.created_by:
            if self.object.current_amount > self.object.target_amount * Decimal('0.25'):
                return render(request, "projects/delete_restricted.html", {
                    "message": "Delete is restricted for the current user."
                })

        return super().dispatch(request, *args, **kwargs)


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_project = self.object
        user = self.request.user
        context["similar_projects"] = Project.objects.filter(
            tags__in=current_project.tags.all()
        ).exclude(id=current_project.id).distinct()[:4]
        context["user"] = self.request.user   # Get the logged-in user
        context["form"] = CommentForm()
        
        # Add rating form and user's existing rating if available
        context["rating_form"] = RatingForm()
        context["rating_count"] = current_project.ratings.count()
        
        # Check if user has already rated this project
        if self.request.user.is_authenticated:
            try:
                user_rating = Rating.objects.get(project=current_project, user=self.request.user)
                context["user_rating"] = user_rating.value
            except Rating.DoesNotExist:
                context["user_rating"] = None
                

        # New: logic to enable/disable delete button
        if user.is_authenticated:
            if user == current_project.created_by and current_project.current_amount > current_project.target_amount * Decimal('0.25'):
                context['can_delete'] = False
            else:
                context['can_delete'] = True
        else:
            context['can_delete'] = False

        return context


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Add user for template convenience
        context["user"] = user

        # For each project, add can_delete flag
        if user.is_authenticated:
            for project in context['object_list']:
                # Superusers can delete any project at any time
                if user.is_superuser:
                    project.can_delete = True
                # Normal users can delete only their own projects if <= 25% funded
                else:
                    project.can_delete = (user == project.created_by and
                                        project.current_amount <= project.target_amount * Decimal('0.25'))
        else:
            for project in context['object_list']:
                project.can_delete = False

        return context



def projects_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    projects = Project.objects.filter(category=category)

    user = request.user

    for project in projects:
        if user.is_authenticated:
            if user.is_superuser:
                project.can_delete = True
            else:
                project.can_delete = (user == project.created_by and
                                    project.current_amount <= project.target_amount * Decimal('0.25'))
        else:
            project.can_delete = False


    return render(request, 'projects/projects_by_category.html', {
        'category': category,
        'projects': projects
    })

class LatestProjectsView(ListView):
    model = Project
    template_name = 'projects/latest_projects.html'
    context_object_name = 'projects'
    queryset = Project.objects.filter(is_active=True).order_by('-start_time')[:5]


@login_required
def rate_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Handle DELETE request to remove a rating
    if request.method == 'DELETE':
        try:
            rating = Rating.objects.get(project=project, user=request.user)
            rating.delete()
            return JsonResponse({
                'success': True,
                'average_rating': project.average_rating(),
                'rating_count': project.ratings.count(),
                'user_rating': 0
            })
        except Rating.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No rating found to delete'}, status=404)
    
    if request.method == 'POST':
        # Check if user has already rated this project
        try:
            rating = Rating.objects.get(project=project, user=request.user)
            form = RatingForm(request.POST, instance=rating)
        except Rating.DoesNotExist:
            form = RatingForm(request.POST)
            
        if form.is_valid():
            rating = form.save(commit=False)
            rating.project = project
            rating.user = request.user
            rating.save()
            
            # Return JSON response with updated rating info
            return JsonResponse({
                'success': True,
                'average_rating': project.average_rating(),
                'rating_count': project.ratings.count(),
                'user_rating': rating.value
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
class FeaturedProjectsView(ListView):
    model = Project
    template_name = 'projects/featured_projects.html'
    context_object_name = 'projects'
    queryset = Project.objects.filter(is_active=True, featuredproject__isnull=False).order_by('-start_time')[:5]
