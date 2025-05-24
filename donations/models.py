from django.db import models
from django.conf import settings
from projects.models import Project

class Donation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donations')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='donations')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} donated ${self.amount} to {self.project.title}"