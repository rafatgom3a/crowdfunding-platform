from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from categories.models import Category
from django.utils import timezone
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class ProjectImage(models.Model):
    project = models.ForeignKey(
        'Project', related_name='project_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="projects/image/")

    def __str__(self):
        return f"Image {self.id}"


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(default=timezone.now)
    # images = models.ManyToManyField(ProjectImage)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    is_active = models.BooleanField(default=True)

    def check_cancellation(self):
        if self.current_amount < self.target_amount * Decimal(0.25):
            self.is_active = False
            self.save()

    def can_be_deleted_by(self, user):
        # Staff can always delete
        if user.is_staff:
            return True
        # Creator can delete only if current_amount <= 25% target_amount
        if user == self.created_by and self.current_amount <= self.target_amount * Decimal('0.25'):
            return True
        return False

    def average_rating(self):
        avg_rating = self.ratings.aggregate(avg=models.Avg('value'))['avg']
        return round(avg_rating, 1) if avg_rating else 0

    def __str__(self):
        return self.title


class Rating(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    value = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"], name="unique_user_rating")
        ]

    def __str__(self):
        return f"{self.project.title} - {self.value} stars"

class Report(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['user', 'content_type', 'object_id'], name='unique_user_report')
        ]

    def __str__(self):
        return f"Report by {self.user.email} on {self.content_type.name} {self.object_id}"