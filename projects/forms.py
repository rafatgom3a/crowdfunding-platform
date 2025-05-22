from django import forms
from .models import Project, ProjectImage, Rating
from django.forms import modelformset_factory

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description", "category", "tags", "target_amount", "end_time"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-control"}),
            "target_amount": forms.NumberInput(attrs={"class": "form-control"}),
            "end_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["value"]
        widgets = {
            "value": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 5}),
        }


class ProjectImageForm(forms.ModelForm):
    class Meta:
        model = ProjectImage
        fields = ['image']



ProjectImageFormSet = modelformset_factory(ProjectImage, form=ProjectImageForm, extra=3)