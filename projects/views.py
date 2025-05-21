# from django.shortcuts import render
# from django.http import HttpResponse

# def home_view(request):
    # For now, let's return a simple HttpResponse
    # Later, you'll render a template here
    # return render(request, 'projects/home.html', {'title': 'Homepage'})
    # Or, for a very basic test:
    # return HttpResponse("<h1>Welcome to the Crowdfunding Platform Home!</h1>")
# Create your views here.



from django.shortcuts import render

from categories.models import Category

def home_view(request):
    categories = Category.objects.all() 
    context = {
        'title': 'Homepage',
        'categories': categories,
    }
    return render(request, 'projects/home.html', context)