from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from projects.models import Project
from .models import Donation
from .forms import DonationForm

@login_required
def donate_to_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.user = request.user
            donation.project = project
            donation.save()
            return render(request, 'donations/donation_success.html', {'donation': donation})
    else:
        form = DonationForm()
    return render(request, 'donations/donate_form.html', {'form': form, 'project': project})

@login_required
def donation_success(request):
    return render(request, 'donations/donation_success.html')