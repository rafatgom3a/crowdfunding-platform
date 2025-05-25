from django.contrib import admin
from .models import Project, Tag, ProjectImage, Rating, Report

admin.site.register(Project)
admin.site.register(Tag)
admin.site.register(ProjectImage)
admin.site.register(Rating)
admin.site.register(Report)
