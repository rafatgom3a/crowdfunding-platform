from django.db import models
from django.shortcuts import get_list_or_404
from django.urls import reverse


# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True )
    description = models.CharField(max_length=100,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)


    def __str__(self):
        return f"{self.name}"
    


    
    # @staticmethod
    # def get_all_categories():
    #     return Category.objects.all()
    

    

    # @staticmethod
    # def get_category_by_id(id):
    #  return get_list_or_404(Category, pk=id)

     
    
    # @property
    # def show_url(self):
    #  return reverse("categories.show", args= [self.id])    
    
    # @property
    # def delete_url(self):
    #  return reverse('category_delete', args=[self.id])  
    

    # @property
    # def edit_url(self):
    #  return reverse('category_edit', args=[self.id])
    