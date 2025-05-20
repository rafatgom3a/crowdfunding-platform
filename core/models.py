from django.db import models
from projects.models import Project, Category
# Create your models here.

class FeaturedProject(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
