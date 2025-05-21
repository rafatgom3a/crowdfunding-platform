# from django.shortcuts import render
# from django.http import HttpResponse

# def home_view(request):
    # For now, let's return a simple HttpResponse
    # Later, you'll render a template here
    # return render(request, 'projects/home.html', {'title': 'Homepage'})
    # Or, for a very basic test:
    # return HttpResponse("<h1>Welcome to the Crowdfunding Platform Home!</h1>")
# Create your views here.



from django.shortcuts import render

from categories.models import Category

def home_view(request):
    categories = Category.objects.all() 
    context = {
        'title': 'Homepage',
        'categories': categories,
    }
    return render(request, 'projects/home.html', context)

from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Project
from .forms import ProjectForm

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"
    success_url = reverse_lazy("projects:list")

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"
    success_url = reverse_lazy("projects:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.check_cancellation()  
        return response

class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = "projects/project_confirm_delete.html"
    success_url = reverse_lazy("projects:list")

class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_project = self.object
        context["similar_projects"] = Project.objects.filter(
            tags__in=current_project.tags.all()
        ).exclude(id=current_project.id).distinct()[:4]
        return context

class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
