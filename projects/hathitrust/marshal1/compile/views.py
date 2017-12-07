from django.shortcuts import get_object_or_404, render
#from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

# Create your views here.
class IndexView(generic.ListView):
    template_name = 'compile/index.html'
    context_object_name = 'list_precompiled_items'
