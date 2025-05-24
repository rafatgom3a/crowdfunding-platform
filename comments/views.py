from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from projects.models import Project
from .models import Comment
from .forms import CommentForm

@login_required
def add_comment(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.project = project
            comment.save()
            return redirect('projects:project_detail', project_id=project.id)
    else:
        form = CommentForm()
    return render(request, 'comments/comment_form.html', {'form': form, 'project': project})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    project_id = comment.project.id
    if request.method == 'POST':
        comment.delete()
        return redirect('projects:project_detail', project_id=project_id)
    return render(request, 'comments/delete_comment_confirm.html', {'comment': comment, 'project_id': project_id})