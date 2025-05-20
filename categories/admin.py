# from categories.models import Category
# Register your models here.
# admin.site.register(Category)

from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')