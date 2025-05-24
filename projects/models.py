from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from categories.models import Category
from django.utils import timezone
from decimal import Decimal

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class ProjectImage(models.Model):
    project = models.ForeignKey('Project', related_name='project_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="projects/image/")

    def __str__(self):
        return f"Image {self.id}"

class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(default=timezone.now)  
    # images = models.ManyToManyField(ProjectImage)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    is_active = models.BooleanField(default=True)

    def check_cancellation(self):
        if self.current_amount < self.target_amount *Decimal(0.25):
            self.is_active = False
            self.save()

    def average_rating(self):
        avg_rating = self.ratings.aggregate(avg=models.Avg('value'))['avg']
        return round(avg_rating, 1) if avg_rating else 0

    def __str__(self):
        return self.title

class Rating(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    value = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["project", "user"], name="unique_user_rating")
        ]

    def __str__(self):
        return f"{self.project.title} - {self.value} stars"
