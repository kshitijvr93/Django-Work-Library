# Create your views here.
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required

from .models import Item

def detail (request, item_id):
    item = get_object_or_404(Item, pk=item_id)

def home(request):

    msg = ("UFDC Cuba Libro Project Home:")

    #admin_href = "localhost:8000/admin/hathitrust"
    #msg += "</br><a href='{}''>Hathitrust Administration</a>".format(admin_href)
    context = {
        'msg' : msg,
    }
    #return HttpResponse(template.render(context, request))
    return render(request, "cuba_libro/home.html", context)
def index(request):

    msg = ("UFDC Cuba Libro Project Index:")

    #admin_href = "localhost:8000/admin/hathitrust"
    #msg += "</br><a href='{}''>Hathitrust Administration</a>".format(admin_href)
    context = {
        'msg' : msg,
    }
    #return HttpResponse(template.render(context, request))
    return render(request, "cuba_libro/index.html", context)


@login_required
def home(request):
    return render(request, 'cuba_libro/home.html')
