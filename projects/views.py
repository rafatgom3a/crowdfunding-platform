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
                # User can delete if they are creator and current_amount <= 25% of target
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


class FeaturedProjectsView(ListView):
    model = Project
    template_name = 'projects/featured_projects.html'
    context_object_name = 'projects'
    queryset = Project.objects.filter(is_active=True, featuredproject__isnull=False).order_by('-start_time')[:5]
