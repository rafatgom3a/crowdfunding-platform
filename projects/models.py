from django.db import models
from django.contrib.auth.models import User  # to track who rated

class Category(models.Model):
    name = models.CharField(max_length=100)

class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_running = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Rating(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField()

    class Meta:
        unique_together = ('project', 'user')  # prevent duplicate ratings per user/project

    def __str__(self):
        return f"{self.project.title} - {self.value} stars"
