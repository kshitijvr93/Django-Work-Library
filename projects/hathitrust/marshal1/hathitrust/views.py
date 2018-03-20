from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Item

def index(request):

    latest_item_list = Item.objects.order_by('-modify_date')[:5]
    template = loader.get_template('hathitrust/index.html')

    msg = ("UFDC Hathitrust Project:")
    msg += ("\nLatest item modified is '{}'"
        .format(latest_item_list[0].name))

    #admin_href = "localhost:8000/admin/hathitrust"
    #msg += "</br><a href='{}''>Hathitrust Administration</a>".format(admin_href)
    context = {
        'latest_item_list' : latest_item_list,
        'item_count' : len(latest_item_list),
    }
    return HttpResponse(template.render(context, request))

# Create your views here.
