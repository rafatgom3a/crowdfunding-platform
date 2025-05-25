from django import forms
from .models import Project, ProjectImage, Rating, Tag
from django.forms import modelformset_factory

class ProjectForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "data-role": "tagsinput",  # This will be used for the tags input library
            "placeholder": "Add tags (comma separated)"
        }),
        help_text="Add comma separated tags"
    )

    class Meta:
        model = Project
        fields = ["title", "description", "category", "target_amount", "end_time"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "category": forms.Select(attrs={"class": "form-select"}),
            # "tags": forms.SelectMultiple(attrs={"class": "form-control"}),
            "target_amount": forms.NumberInput(attrs={"class": "form-control"}),
            "end_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Set initial value for tags as comma-separated string
            self.fields['tags'].initial = ', '.join(tag.name for tag in self.instance.tags.all())

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        # Split tags by comma and strip whitespace
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        return tag_list

    def save(self, commit=True):
        project = super().save(commit=commit)
        tag_names = self.cleaned_data['tags']
        
        # Clear existing tags
        project.tags.clear()
        
        # Add new tags
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            project.tags.add(tag)
        
        return project

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