from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader

def detail (request, item_id):
    item = get_object_or_404(Item, pk=item_id)

def index(request):


    msg = ("UF Library Marshaling Application Website")

    #admin_href = "localhost:8000/admin/hathitrust"
    #msg += "</br><a href='{}''>Hathitrust Administration</a>".format(admin_href)
    context = {
        'msg' : msg,
    }
    #return HttpResponse(template.render(context, request))
    return render(request, "maw_home/index.html", context)

# Create your views here.
