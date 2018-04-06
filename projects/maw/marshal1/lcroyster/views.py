from django.shortcuts import get_object_or_404, render, render_to_response

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from .models import Project, Location, Sensor, SensorDeploy, WaterObservation

from django.forms import TextInput, Textarea
from django.conf import settings

def detail (request, item_id):
    item = get_object_or_404(Item, pk=item_id)

def index(request):
    latest_item_list = Item.objects.order_by('-modify_date')[:5]

    msg = ("UF Libraries MAW Lcroyster Project:")
    msg += ("\nLatest item modified is '{}'"
        .format(latest_item_list[0].name))

    #admin_href = "localhost:8000/admin/hathitrust"
    #msg += "</br><a href='{}''>Hathitrust Administration</a>".format(admin_href)
    context = {
        'latest_item_list' : latest_item_list,
        'item_count' : len(latest_item_list),
    }
    #return HttpResponse(template.render(context, request))
    return render(request, "lcroyster/index.html", context)
# end def index()

from django import forms
from django.contrib.auth.decorators import login_required
