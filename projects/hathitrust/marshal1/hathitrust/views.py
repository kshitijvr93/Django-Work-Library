from django.shortcuts import render
from django.http import HttpResponse
from .models import Item

def index(request):

    latest_items_list = Item.objects.order_by('-modify_date')[:5]

    msg = ("UFDC Hathitrust Project:")
    msg += ("\nLatest item modified is '{}'"
        .format(latest_items_list[0].name))

    #admin_href = "localhost:8000/admin/hathitrust"
    #msg += "</br><a href='{}''>Hathitrust Administration</a>".format(admin_href)
    return HttpResponse(msg)

# Create your views here.
