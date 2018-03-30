from django.shortcuts import get_object_or_404, render, render_to_response

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from .models import Item, File
from django.forms import TextInput, Textarea

def detail (request, item_id):
    item = get_object_or_404(Item, pk=item_id)

def index(request):
    latest_item_list = Item.objects.order_by('-modify_date')[:5]

    msg = ("UFDC Hathitrust Project:")
    msg += ("\nLatest item modified is '{}'"
        .format(latest_item_list[0].name))

    #admin_href = "localhost:8000/admin/hathitrust"
    #msg += "</br><a href='{}''>Hathitrust Administration</a>".format(admin_href)
    context = {
        'latest_item_list' : latest_item_list,
        'item_count' : len(latest_item_list),
    }
    #return HttpResponse(template.render(context, request))
    return render(request, "hathitrust/index.html", context)
# end def index()

from django import forms
from django.contrib.auth.decorators import login_required

class FormUploadFile(forms.Form):
    description = forms.CharField(required=False
           ,widget=forms.widgets.Textarea()
        )

    topic = forms.CharField(max_length=128,required=False,
      widget=TextInput( attrs={'size':'100'}))
    down_name = forms.CharField(max_length=128,required=False,
      widget=TextInput( attrs={'size':'100'}))

    # Note: do NOT define widget 'TextInput' params here else the
    # required FileField widget with the Browse button is overridden.
    file  = forms.FileField(max_length=128,
        # widget=TextInput( attrs={'size':'100'})
      )
# end class FormUploadFile

def upload_success(request, file_id):

    template_file= 'hathitrust/upload_success.html'
    message = ( "You succeeded uploading your file_id = '" + file_id
        + "' ! Congratulations!")
    rendered = render(request, template_file,
        { 'a' : 'a', 'main_left' : message })

    return HttpResponse(rendered)

#end def upload_success}}}

def handle_uploaded_file(ufo, form):
    """
    Param ufo is an UploadedFileObject (see Django Docs)
    which has in Django 1.1 the contents of the uploaded file (into Django
    "chunks"), attributess of name, size, chunks, content_type.

    Param form is the form that was used (see FormUploadFile) to prompt user
    for some file attributes (eg location of file on browsing machine,
    preferred name for future downloads of the copy that will be stored on
    the server) before uploading is allowed.

    Note below that we must use the form.cleaned_data dictionary to
    access the form data. Also, though the user uses a widget to select
    a file to upload, and its original filename appears on the form after a
    file is selected, that name is not contained in the form object proper,
    but rather it is available in the ufo.

    Note: In the future, an sha512 index (or some other good hash) should
    be generated here and checked to see whether the file has already been
    uploaded, and if not, then check a quota system for N of bytes limit
    for the uploading Department.

    If the ufo file_data chunks are to be written to the local file below,
    then a files_quota row should be updated with the incremented N of bytes
    used for a department.
    """

    #If the form provdes no name for future downloads of this file, reuse the
    # original ufo.name that was used on the uploading machine for the file.
    down_filename = form.cleaned_data['down_name']
    if not down_filename:
        down_filename = ufo.name

    # set down_filename }}}
    # {{{ set topic_value

    # if topic_value is None, use the down_name with periods and underbars removed.
    # since topic is a search field, this will 'reveal' component keywords to enable
    # more search keyword hits in future searches for this row.

    topic_value=form.cleaned_data['topic']
    if not topic_value:
        topic_value = down_filename
        topic_value = topic_value.replace('.', ' ')
        topic_value = topic_value.replace('_', ' ')

    # create a row in model "File" to represent this uploaded file.
    file = File(department='rvp'
           #,date_time=datetime.datetime.now()
           ,up_name=ufo.name
           ,down_name=down_filename
           ,size=ufo.size
    	   #,topic=form.cleaned_data['topic']
    	   ,topic=topic_value
           ,content_type=ufo.content_type
           ,charset=ufo.charset
           ,sha512="sha512_hex_bytes_here"
           )
    #must save the row before getting its id
    file.save()
    id = file.id

    # create saved file name in MEDIA_URL, simply named by the file id.
    file_dir=r'U:\\django\\data\\hathitrust\\files\\'
    pathname = ("{}file_{}"
       .format(file_dir, id))

    #open the file for writing, write the ufo.chunks of file content into it.
    destination = open(pathname, 'wb+')
    for chunk in ufo.chunks():
        destination.write(chunk)
    destination.close()

    # Set the file's now-established server url and save it.
    # Then we are done except for some wrap-up.
    # set the url for future downloads of this server-saved file:
    url = "%s%d" % ("https://robertvernonphillips.com/files/download/", id)
    file.url = url

    anchor_html = '<html><body>[<a href="' + url + '">click here</a>]'

    file.description = ( anchor_html + form.cleaned_data['description']
        + "</body></html>" )

    file.save()
    return file.id

# end def handle_uploaded_file()

#NB: def file_upload() depends on FormUploadFile,handle_uploaded_file,
# upload_success

# upload a file that a user selects on the client web browser's machine
@login_required
def file_upload(request, file_id='tmp'):
    if request.method == 'POST':
        # We have to pass request.FILES into the form's constructor; this is
        # how file data gets bound into a form.
        form = FormUploadFile(request.POST, request.FILES)
        if form.is_valid():
            file_id = handle_uploaded_file(request.FILES['file'],form)
            return HttpResponseRedirect('/hathitrust/upload/success/' + str(file_id) + '/')
    else:
        form = FormUploadFile()
    # Per https://stackoverflow.com/questions/41606754/django-csrf-token-generation-render-to-response-vs-render
    # Avoid and replace the deprecated (now commented out) next line.
    # return render_to_response('hathitrust/upload.html', {'form': form,})
    return render(request, 'hathitrust/upload.html', {'form': form,})

# depends on FormUploadFile, handle_uploaded_file, upload_success
@login_required
def file_download(request, file_id):
    row_list = ''

    #{{{ If user may, get the file row corresponding to the file_id.
    #NOTE: the user data appears to be hosted in a client cookie, and the side effect is that it is dependent on domain NAME, not domain IP address, so if one is using a browser tab visiting lawcloud.com and another tab is visiting robertvernonphillips.com, and a link on the latter page is for the former page then by visiting the 'other' domain name, though the IP is the same, the same physical user appears to be a different user  due to different user cookies, set per domain name.
    if not request.user.is_staff:
      # if user is not staff, must filter for only public files
      row_list = list(ModelFile.objects.filter(id = file_id).filter(public=True))
    else:
      #{{{ get the file row corresponding to the file_id
      row_list = list(ModelFile.objects.filter(id = file_id))
    #}}}

    if not row_list:
       msg =""
       msg=msg + "Download file_id=" + str(id) + "for first_name='" + request.user.first_name +"', "
       msg=msg + "is_authenticated()='" + str(request.user.is_authenticated()) +"', "
       msg=msg + "is_active='" + str(request.user.is_active)  + "', "
       msg=msg + "is_staff='" + str(request.user.is_staff)  + "', "
       msg=msg + "is_superuser='" + str(request.user.is_superuser) +"'."
       msg=msg+ "</br>You are not logged in with permission to see your requested link. </br>You may close this page. Please try another link."
       return HttpResponse(msg)

    filerow = row_list[0]

    #{{{ future: do this for mod_xsendfile:
    # Create response with proper mimetype
    # response = HttpResponse(mimetype='application/force-download')
    #response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    # response['X-Sendfile'] = smart_str(path_to_file)
    # response['X-Sendfile'] = smart_str(path_to_file)
    #}}}
    #{{{ Set response headers properly to serve this file.

    # quick first cut - though Django is not as efficient, use to start.
    # set the content_type that django set at upload from the file suffix.
    response = HttpResponse(mimetype = filerow.content_type)

    # set the downloaded file name
    # if filerow has no download name, set it to the same name as the
    #uploader used to upload the file
    #sample:response['Content-Disposition'] = 'attachment; filename=fatdog.jpg'
    if filerow.down_name == "":
      att_info = 'attachment; filename='  + filerow.up_name
    else:
      att_info = 'attachment; filename='  + filerow.down_name

    #if filerow has no topic, set it to the same as the download name,
    #except change all underbars and periods to spaces to keywords are apparent for searches.

    response['Content-Disposition'] = att_info
    #}}}
    #{{{ Use Django to read the source file and write it into the response
    # the file name is rooted in priv (get this from settings.py later)
    root_path = '/c/home/rvp/dj1.1/mysite/priv'

    fs_name = root_path + '/files/file_' + str(filerow.id)

    #open the file for reading, create and return a response object.
    source = open(fs_name, 'rb');

    # for chunk in source.chunks():
    response.write(source.read())
    source.close()
    #}}}
    return response
# end file_download()

# def public()
# depends on FormUploadFile,handle_uploaded_file,upload_success
# NOTE: NO login is required here, so take care now to hand-code to only allow
# public fiiles to be identified here.
def public(request, file_id):
    '''
    Seek an uploaded file_id that is marked as public and if so, download it.
    '''
    # get the file row corresponding to the file_id
    # file_id ignored for now - just set to 1 particular file
    row_list = list(ModelFile.objects.filter(id = file_id).filter(public=True))
    # insert test here whether row_list[0] is None - if so, give file not found
    # or simply return nothing or redirect?
    filerow = row_list[0]

    # future: do this for mod_xsendfile:
    # Create response with proper mimetype
    # response = HttpResponse(mimetype='application/force-download')
    #response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    # response['X-Sendfile'] = smart_str(path_to_file)
    # response['X-Sendfile'] = smart_str(path_to_file)
    #}}}
    #{{{ Set response headers properly to serve this file.

    # quick first cut - though Django is not as efficient to serve static files,
    # still use to start.
    # set the content_type that django set at upload from the file suffix.
    response = HttpResponse(mimetype = filerow.content_type)

    # set the downloaded file name
    # if filerow has no download name, set it to the same name as the
    #uploader used to upload the file
    #sample:response['Content-Disposition'] = 'attachment; filename=fatdog.jpg'
    if filerow.down_name == "":
      att_info = 'attachment; filename='  + filerow.up_name
    else:
      att_info = 'attachment; filename='  + filerow.down_name
    #
    response['Content-Disposition'] = att_info

    # Use Django to read the source file and write it into the response
    # the file name is rooted in priv (get this from settings.py later)
    root_path = '/c/home/rvp/data/priv'

    fs_name = root_path + '/files/file_' + str(filerow.id)

    #open the file for reading, create and return a response object.
    source = open(fs_name, 'rb');
    # 091125- dj1.1, got attrib error, file object has no 'chunks', so shelve:
    # for chunk in source.chunks():
    response.write(source.read())
    source.close()
    #}}}
    return response
# end def public()
