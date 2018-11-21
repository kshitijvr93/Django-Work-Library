from django.shortcuts import get_object_or_404, render, render_to_response

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from .models import Item, File, UploadFile

from django.forms import TextInput, Textarea
from django.conf import settings
from multiprocessing import Process
import os, sys
from time import sleep

# meta_yaml - initial test yaml file
meta_yaml_example = '''# This is an example meta.yml file that provides additional metadata used for
# ingesting material into HathiTrust. This file must be a well-formed YAML file.
# See the YAML specification for more information:
#
# http://www.yaml.org/spec/1.2/spec.html
#
# Lines that start with a # character are comments.

####### FOR MATERIAL SCANNED FROM PRINT ONLY ##########################################
# Required - the date and approximate time the volume was scanned. This date
# will be used for the PREMIS capture event. It will also be used to populate
# the ModifyDate TIFF header and XMP tiff:DateTime image headers if they are
# missing in the submitted images.
#
# This must be in the ISO8601 combined date format with time zone
# (see https://en.wikipedia.org/wiki/ISO_8601#Combined_date_and_time_representations)
#
# Note: the -05:00 is a representation of a time zone offset from UTC, not
# a representation of a time range.
capture_date: 2013-11-01T12:31:00-05:00

# If the submitted images are missing information about the scanner make and
# model (XMP tiff:Make and tiff:Model header) it can be supplied here. It will
# only be used if the submitted images do not have the scanner make.  This
# element is optional.
scanner_make: CopiBook
scanner_model: HD

# If the submitted images do not have the TIFF Artist or XMP tiff:Artist
# header, this value must be supplied. It should reflect "who pushed the
# button" to actually scan the item. This could be an organizational unit or an
# outside vendor. It will only be used if the submitted images are missing the
# TIFF Artist and XMP tiff:Artist headers.
scanner_user: "University of Michigan: Digital Conversion Unit"

############## END OF SECTION FOR MATERIAL SCANNED FROM PRINT #####################

####### FOR BORN DIGITAL MATERIAL ONLY ##########################################

# Required: date the digital file this submission was created from was created.
# For example, suppose a university press provides a born-digital PDF file for ingest
# into HathiTrust. Record the creation date of that PDF here.
creation_date: 2013-10-01T12:23:42-05:00

# Required: HathiTrust organization code of who created the digital file. This is
# typically the organization-specific part of the domain name. If the organization code
# is unknown, contact HathiTrust staff.
creation_agent: knowledgeunlatched

# Optional: If there is a "content provider" of the digital item that differs per
# item in the submission batch, record the HathiTrust organization code here. For
# example, if several different publishers provided digital files to Michigan that were
# prepared for ingest into HathiTrust, the publisher would be recorded here. Most of
# the time, this will be the same as the creation agent.
digital_content_provider: dukeupress

# If the submitted images do not have the TIFF Artist or XMP tiff:Artist header, this
# value must be supplied. It should reflect who created the original born digital item.
# Frequently this will be the author or publisher of the item. It will only be used if
# the submitted images are missing the TIFF Artist and XMP tiff:Artist headers.
tiff_artist: "Duke University Press"
######## END OF SECTION FOR BORN DIGITAL MATERIAL     ###########################


##############FOR ALL MATERIAL####################################################

# If the submitted images are missing resolution information, the resolution must
# be supplied here. It will only be used if the submitted images do not contain
# resolution information.

# Resolution for bitonal TIFFs
bitonal_resolution_dpi: 600
# Resolution for contone TIFFs or JPEG2000 images
contone_resolution_dpi: 300

# If the images were compressed, converted, or normalized before SIP
# generation, these values should be supplied. The date must be in ISO8601
# combined date format and the agent must be a HathiTrust organization code.
# The tools should list the software tool names and versions.

image_compression_date: 2013-11-01T12:15:00-05:00
image_compression_agent: umich
image_compression_tool: ["kdu_compress v7.2.3","ImageMagick 6.7.8"]

# If this volume was scanned right-to-left and/or should read right-to-left,
# put "right-to-left" for the scanning or reading order here. If this information
# is not provided, volumes are assumed to be scanned left-to-right and read
# left-to-right. For born digital material, "scanning order" really means
# "rasterization order".

# The possibilities are:
#
# Book reads left-to-right and 00000001.tif is the FRONT cover of the book:
#   scanning_order: left_to_right; reading_order: left_to_right
# Book reads left-to-right but 00000001.tif is the BACK cover of the book:
#   scanning_order: right_to_left; reading_order: left_to_right
# Book reads right-to-left and 00000001.tif is the FRONT cover of the book:
#   scanning_order: right_to_left; reading_order: right_to_left
# Book reads right-to-left but 00000001.tif is the BACK cover of the book:
#   scanning_order: left_to_right; reading_order: right_to_left
#
# For more complicated cases (e.g. books that are half in English and half in Hebrew and
# are read either left to right or right to left, or books that are in two left-to-right
# languages and one language is printed upside-down from the other), pick the correct
# scanning order and one of the correct reading orders. Users of the other language can
# use the interface to adjust the view appropriately.
scanning_order: left-to-right
reading_order: left-to-right

# Optionally, page numbers and page tag data can be supplied here.
# The orderlabel is the page number and the label is the page tag.
# Multiple page tags should be comma-separated.
#
# Allowable page tags include:
#
# BACK_COVER - Image of the back cover
#
# BLANK - An intentionally blank page.
#
# CHAPTER_PAGE - A sort of half title page for a chapter of grouping of
# chapters -- that is, a page that gives the name of the chapter or section
# that begins on the next page.
#
# CHAPTER_START - Subsequent chapters with regular page numbering after the
# first. Also use this for the beginning of each appendix.
#
# COPYRIGHT - Title page verso (the back of the real title page)
#
# FIRST_CONTENT_CHAPTER_START - First page of the first chapter with regular
# page numbering. If the first chapter with regular numbering is called the
# introduction, that's okay.
#
# FOLDOUT - A page that folded out of the print original
#
# FRONT_COVER - Image of the front cover (if the cover of the book was scanned)
#
# IMAGE_ON_PAGE - Use for plates (pages with only images, which often do not
# contain the regular page numbering)
#
# INDEX - The first page in a sequence containing an index
#
# MULTIWORK_BOUNDARY: for items with multiple volumes bound together
#
# PREFACE - First page of each section that appears between the title page
# verso and the first regularly numbered page. For example, a one-page
# dedication on page xvi would get this tag, and then the first page of a
# three-page preface starting on page xviii would also get this.  However, if
# the introduction of the text starts on page 1 (or on an unnumbered page
# followed by page 2), do not use this tag. Use for components occurring before
# and after the table of contents.
#
# REFERENCES - The first page in a sequence containing endnotes or a
# bibliography
#
# TABLE_OF_CONTENTS - First page of the table of contents
#
# TITLE - Title page recto (the front of the real title page)
#
# TITLE_PARTS - Half title page (a sort of preliminary title page before the
# real one)
#
# Please contact HathiTrust staff for additional guidance in mapping your page tags
# to HathiTrust conventions.
#
# Note: the indentation here must use only spaces, never tabs: see
# http://www.yaml.org/spec/1.2/spec.html#id2777534

pagedata:
  00000001.jp2: { label: "FRONT_COVER" }
  00000007.jp2: { label: "TITLE" }
  00000008.jp2: { label: "COPYRIGHT" }
  00000009.jp2: { orderlabel: "i", label: "TABLE_OF_CONTENTS" }
  00000010.jp2: { orderlabel: "ii", label: "PREFACE" }
  00000011.jp2: { orderlabel: "iii" }
  00000012.jp2: { orderlabel: "iv" }
  00000013.jp2: { orderlabel: "v" }
  00000014.jp2: { orderlabel: "vi" }
  00000015.jp2: { orderlabel: "1", label: "FIRST_CONTENT_CHAPTER_START" }
  00000016.jp2: { orderlabel: "2" }
  00000017.jp2: { orderlabel: "3" }
  00000018.jp2: { orderlabel: "4", label: "IMAGE_ON_PAGE" }

'''

meta_yaml_test = '''#HathiTrust-compliant meta.yml file
capture_date: {capture_date}
scanner_user: "University of Florida, George A. Smathers Libraries: Digital Production Services"
'''

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

# class FormUploadFile(forms.Form):
#
# Purpose: derive from ModelForm so admin can use it to add...
# See view method file_upload() which uses this form
# does. It has been useful since using it in 2009 to serve a model "File",
# and in 2018 it is modified  to use new model "UploadFile"
# See also django 2.0 implementation of 2018 now for model "File"
# and its admin and form, and associated code.
# This is less featured than the 2009 version, but adequate for many uses, and
# it is uses now-'standard' supported django 2.0 features so it can be used by
# django standard admin.
#
class FormUploadFile(forms.ModelForm):

    description = forms.CharField(required=False
           ,widget=forms.widgets.Textarea()
        )
    #{ See https://stackoverflow.com/questions/29112847/the-value-of-form-must-inherit-from-basemodelform
    class Meta:

        model = UploadFile
        # https://stackoverflow.com/questions/36953940/creating-a-modelform-without-either-the-fields-attribute-or-the-exclude-attr
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(FormUploadFile, self).__init__(*args, **kwargs)
    #} See https://stackoverflow.com/questions/29112847/the-value-of-form-must-inherit-from-basemodelform

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

import os
import maw_settings


def gen_batch_packages(request):
    '''

    '''

    pass
# end def gen_batch_packages()

def upload_success(request, file_id):

    template_file= 'hathitrust/upload_success.html'
    message = (
        "You succeeded uploading file '{}{}'! Congratulations!"
        .format(settings.MEDIA_ROOT,file_id))
    rendered = render(request, template_file,
        { 'a' : 'a', 'main_left' : message })

    return HttpResponse(rendered)

#end def upload_success}}}

def handle_uploaded_file(ufo, form):
    """

    Param ufo is an UploadedFileObject (see Django Docs)
    which has in Django 1.1 the contents of the uploaded file (into Django
    "chunks"), attributes of name, size, chunks, content_type.

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
    file_dir = settings.MEDIA_ROOT
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
    media_url_path = "files/download/{}".format(id)
    file.url = media_url_path

    anchor_html = ('<html><body>[<a href="{}{}">click here</a>'
        .format(settings.MEDIA_URL,media_url_path))

    file.description = ( anchor_html + form.cleaned_data['description']
        + "</body></html>" )

    file.save()
    return file.id

# end def handle_uploaded_file()

# NB: def file_upload() depends on FormUploadFile,handle_uploaded_file,
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
            return HttpResponseRedirect(
                '/hathitrust/upload/success/{}/'.format(file_id))
    else:
        form = FormUploadFile()
    # Per https://stackoverflow.com/questions/41606754/django-csrf-token-generation-render-to-response-vs-render
    # Replace the by django 2.0 deprecated (now commented out) next line.
    # return render_to_response('hathitrust/upload.html', {'form': form,})
    return render(request, 'hathitrust/upload.html', {'form': form,})

# depends on FormUploadFile, handle_uploaded_file, upload_success
@login_required
def file_download(request, file_id):
    row_list = ''

    #NOTE: the user data appears to be hosted in a client cookie, and the side effect is that it is dependent on domain NAME, not domain IP address, so if one is using a browser tab visiting lawcloud.com and another tab is visiting robertvernonphillips.com, and a link on the latter page is for the former page then by visiting the 'other' domain name, though the IP is the same, the same physical user appears to be a different user  due to different user cookies, set per domain name.
    if not request.user.is_staff:
      # if user is not staff, must filter for only public files
      row_list = list(ModelFile.objects.filter(id=file_id).filter(public=True))
    else:
      #{{{ get the file row corresponding to the file_id
      row_list = list(ModelFile.objects.filter(id=file_id))

    if not row_list:
       # No file found, so return some meta info only
       msg =""
       msg=msg + ("Download file_id=" + str(id) + "for first_name='" +
           request.user.first_name +"', ")
       msg=msg + ("is_authenticated()='" +
           str(request.user.is_authenticated()) +"', ")
       msg=msg + "is_active='" + str(request.user.is_active)  + "', "
       msg=msg + "is_staff='" + str(request.user.is_staff)  + "', "
       msg=msg + "is_superuser='" + str(request.user.is_superuser) +"'."
       msg=msg+ ("</br>You are not logged in with permission to see your "
            "requested link. </br>You may close this page. "
            "Please try another link.")
       return HttpResponse(msg)

    #
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
    # set the content_type that django set at upload from the file suffix,
    # or that possibly was changed in the database.
    response = HttpResponse(mimetype=filerow.content_type)

    # set the downloaded file name
    # if filerow has no download name, set it to the same name as the
    # uploader used to upload the file
    #sample:response['Content-Disposition'] = 'attachment; filename=fatdog.jpg'
    if filerow.down_name == "":
      att_info = 'attachment; filename='  + filerow.up_name
    else:
      att_info = 'attachment; filename='  + filerow.down_name

    #if filerow has no topic, set it to the same as the download name,
    #except change all underbars and periods to spaces to keywords are apparent for searches.

    response['Content-Disposition'] = att_info

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
