# from django.shortcuts import render
# from django.http import HttpResponse

# def home_view(request):
    # For now, let's return a simple HttpResponse
    # Later, you'll render a template here
    # return render(request, 'projects/home.html', {'title': 'Homepage'})
    # Or, for a very basic test:
    # return HttpResponse("<h1>Welcome to the Crowdfunding Platform Home!</h1>")
# Create your views here.



from django.shortcuts import get_object_or_404, redirect, render

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
from django import forms
from .models import Project, ProjectImage, Report
from .forms import ProjectForm, ProjectImageFormSet
from comments.forms import CommentForm
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.decorators import login_required


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'category', 'tags', 'target_amount', 'end_time']




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
        ProjectImage.objects.filter(id__in=image_ids_to_delete, project=self.object).delete()

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

class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_project = self.object
        context["similar_projects"] = Project.objects.filter(
            tags__in=current_project.tags.all()
        ).exclude(id=current_project.id).distinct()[:4]
        context["user"] = self.request.user   # Get the logged-in user
        context["form"] = CommentForm()
        return context

class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user  # add logged-in user
        return context


def projects_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    projects = Project.objects.filter(category=category)
    return render(request, 'projects/projects_by_category.html', {
        'category': category,
        'projects': projects
    })


@login_required
def report_content(request, content_type, object_id):
    content_type_obj = get_object_or_404(ContentType, model=content_type)
    content_object = get_object_or_404(content_type_obj.model_class(), id=object_id)
    
    if Report.objects.filter(user=request.user, content_type=content_type_obj, object_id=object_id).exists():
        pass
    else:
        Report.objects.create(
            user=request.user,
            content_type=content_type_obj,
            object_id=object_id
        )
    
    return redirect('projects:detail', pk=content_object.id if content_type == 'project' else content_object.project.id)