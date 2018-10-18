import uuid

from django.db import models
#from django_enumfield import enum
from django.forms import ModelForm, Textarea

#other useful model imports at times (see django docs, tutorials):
import datetime
from django.utils import timezone
from maw_utils import SpaceTextField, SpaceCharField, PlusIntegerField
from mptt.models import MPTTModel, TreeForeignKey

#suppoort per field custom widget sizes for admin and inline admin
from django import forms

from django.contrib.auth import get_user_model
User = get_user_model()

'''
NOTE: rather than have a separate file router.py to host HathiRouter, I just
put it here. Also see settings.py should include this python import dot-path
as one of the listed strings in the list setting for DATABASE_ROUTERS.
'''

# Maybe move the HathiRouter later, but for now keep here
#
class DpsRouter:
    '''
    A router to control all db ops on models in this Application. See apps.py.
    '''

    # Model django_migration database rows use app_label as the 'app' value,
    # and app_label followed by '_', is the db table name prefix
    # for all models of this app.
    app_label = 'dps'

    # Main settings.py file will set up a DATABASES[app_db] dictionary to
    # specify this app's database connectiom.
    app_db = 'dps_connection'

    '''
    See: https://docs.djangoproject.com/en/2.0/topics/db/multi-db/
    For given 'auth' model (caller insures that the model is always an auth
    model ?),  return the db alias name (see main DATABASES setting in
    settings.py) to use.
    '''
    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return self.app_db
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return self.app_db
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (   obj1._meta.app_label == self.app_label
           or  obj2._meta.app_label == self.app_label):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == self.app_label:
            return db == self.app_db
        return None
# end class DpsRouter

# NB: we accept the django default of prefixing each real
# db table name with the app_name.

'''
Consider utility that takes an mptt row-node or a root folder of xml files
and applies an xml2rdb config to gen a zip file of sql creation script to
download to apply to local postgres database.
'''

class Bibvid(models.Model):
    '''
    Use id as unique index
    consider bibvid as alternate unique index that allows NULL because
    may consider items 'being constructed' might not have bibvids assigned.

    Todo: add utility to go ahead and descend the resources directory and
    add a row to this table where the named bibvid folder (...AA12345678/00001)
    exists. Maybe it will also get extra data from sobek, if extant.

    Fields to consider:
      bibid, vid, bibvid(with underbar separator)
      resource_subpath
      counts of various file types, pdf, jpeg, etc.
      total file count, including mets, etc in main folder
      count of subfolders, maybe a count
      mets (foreignkey of a mptt model's row that reps the top node
            of the mets file)
    '''
    id = models.AutoField(primary_key=True)

    bibvid = SpaceCharField(verbose_name='Bibvid AA12345678_NNNNN',
        max_length=255, unique=False, blank=False, null=False, default='bibvid',
        help_text= ("UF Bibvid with 10-character bib, underbar, and 5-digit"
          " vid value."),
        editable=True)

    resource_subpath = SpaceCharField(max_length=255, null=True, default='subpath',
      blank=True, editable=True,
      )
    count_files = models.PositiveIntegerField(default=0,null=False)
    count_pdf = models.PositiveIntegerField(default=0,null=False)
    count_jp2 = models.PositiveIntegerField(default=0,null=False)
    count_jpeg = models.PositiveIntegerField(default=0,null=False)
    count_alto = models.PositiveIntegerField(default=0,null=False)
    count_pro = models.PositiveIntegerField(default=0,null=False)
    count_xml = models.PositiveIntegerField(default=0,null=False)

    note = SpaceTextField(max_length=2550, null=True, default='note', blank=True,
      help_text= ("General note"),
      editable=True,
      )

    def __str__(self):
        return str(self.bibvid)

#end class bibvid

class BatchSet(models.Model):
    '''
    Model BatchSet stores information about a set of BatchItem rows
    that were created via a spreadsheet import operation.
    Fields include an identifier, the username of the user who created the
    import, the date-time of the import.
    Consider to include a count of items imported.

    TODO: Do not allow users to delete rows. The import operations themselves
    are historical data desired for UFDC management.
    '''

    id = models.AutoField(primary_key=True)
    # batch_datetime is time the batch was created/imported
    name = SpaceCharField(verbose_name='Custom Unique Batch Name',
        max_length=255, unique=False, blank=True, null=True, default='',
        db_index=True, help_text= ("Up to 255 characters." ), editable=True)
    notes = SpaceTextField(
        verbose_name='Notes about the imported batch of bib-vids.',
        max_length=3000, unique=False, blank=True, null=True, default='',
        help_text='Optional Notes about the imported batch of bib-vids.',
        editable=True)
    import_datetime = models.DateTimeField('Importing DateTime (UTC)',
        null=False, auto_now=True, editable=False)
    import_username = SpaceCharField(
        verbose_name='User who did the import',
        max_length=255, unique=False, blank=False, null=False, default='',
        db_index=True, help_text= ("Up to 255 characters." ), editable=True)

    import_filename = SpaceCharField(verbose_name='Imported File Name',
        max_length=255, unique=False, blank=False, null=False, default='',
        db_index=True, help_text= ("Up to 255 characters." ), editable=True)
    import_bibfield = SpaceCharField(
        verbose_name='Import field with BibID',
        max_length=255, unique=False, blank=False, null=False, default='BibID',
        help_text= ("Import file's BibID Field Name" ), editable=True)
    # Individual process executions  may query the use whether to interpret
    # devfault vid 00001 as to mean all vids found under UFDC resoures for the
    # bib or the literal one  and only 00001 vid.
    import_vidfield = SpaceCharField(
        verbose_name='Import field with VID',
        max_length=255, unique=False, blank=True, null=True, default='VID',
        help_text= ("Import file's field name for Volume ID (VID). "
            "If empty, value 00001 will be set for the VID value." ),
        editable=True)
    item_count =models.IntegerField(
        verbose_name='Item Count',
        db_index=True,
        unique=False, blank=False, null=False, default=0,
        help_text= ("Count of import bibvid items from the import." ),
        )

    def __str__(self):
        return (
          f"{self.id}, {self.item_count} items from {self.import_filename}")

# end class BatchSet

class BatchItem(models.Model):
    '''
    Model BatchItem stores a UFDC Bib_vid identifier and
    a foreign key to a batch set.
    '''
    # try removing this - maybe it 'spooks' admin impots to be explicit?
    # nope.

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4,
      editable=False)

    # Adding this to quell django import-export complaints about lack
    # of id field
    # id0 = models.AutoField(primary_key=True)

    row_count = models.IntegerField(default=0)

    batch_set = models.ForeignKey('BatchSet', blank=True, null=True,
      db_index=True,
      help_text="Imported BatchSet of which this row is a member.",
      on_delete=models.CASCADE,)

    # Note: delete of 1 effectively allows delete of this item before
    # importing the same item again -- so that would be effectively an UPDATE
    # for such item.
    # TODO: once a batchSet is used with any maw process, should set
    # delete=0 for all items in that batchset. This will freeze the
    # items of the batchset for historical reports. IE, no future import
    # for this batch set may be made, if dup insert errors on import
    # prevent it).
    delete =models.IntegerField(
        verbose_name='Delete on next import of this item?',
        unique=False, blank=False, null=False, default=1,
        help_text= ("1 (delete on next import of this item) or 0 (do not)" ),
        )

    bibid = SpaceCharField(verbose_name='Bibliographic ID', max_length=10,
        unique=False, blank=False, null=False, default='',
        help_text= ("Enter alphabetic characters followed by digit characters"
          " for a total of 10 characters."),
        )

    vid = SpaceCharField(verbose_name='Volume ID', max_length=10,
        unique=False, blank=False, null=False, default='',
        help_text= ("Five digit characters with zeroes on the left. "),
        )

    def __str__(self):
        return str(f"{self.bibid.upper()}_{self.vid}")

    class Meta:
        unique_together = ["batch_set", "bibid","vid"]
        #order_with_respect_to = 'batch_set'
# end class BatchItem

class ThesTree(MPTTModel):
    '''
    A master thesauri tree including all a tree for each thesaurus with terms
    of interest.
    Each row with a null parent value (ie without a parent), is a 'root node'
    of a separate thesaurus tree identified by a row in model Thesaurus

    TODO: Add some custom save() validations
    (1) For added 'root' rows with null parent value:
    The name corresponds to exactly one row's name in model Thesaurus.
    (2) Among all rows with the same parent value (including Null),
    validate that the row name is unique
    '''

    id = models.AutoField(primary_key=True)

    # Only one relation in a schema has a null parent
    parent = TreeForeignKey('self', null=True, blank=True,
      related_name='children', db_index=True,
      verbose_name = "Parent relation",
      on_delete=models.CASCADE,)

    # Note, internally a unique suffix for the relation name
    # NOTE: it must be unique within the snow flake tree
    name = SpaceCharField(verbose_name='Thesaurus term name', max_length=255,
        unique=False, blank=False, null=False, default='name',
        help_text= ("If no parent, name of thesaurus, else the name"
          " for this narrower term under the broader parent.")
        , editable=True)

    def __str__(self):
        return str(self.name)

    class MPTTMeta:
        order_by = ['name']
# end class ThesTree(MPTTModel)

class RelatedTerm(models.Model):
    id = models.AutoField(primary_key=True)

    # Only one relation in a schema has a null parent
    primary_term = models.ForeignKey('ThesTree', blank=False,
      related_name='related_term', db_index=True,
      help_text= "Primary term in thesauri to which this term is related",
      on_delete=models.CASCADE,)

    # Note, internally a unique suffix for the relation name
    # NOTE: it must be unique within the snow flake tree
    name = SpaceCharField(verbose_name='Related term name', max_length=255,
        unique=False, blank=False, null=False, default='name',
        help_text= ("If no parent, name of thesaurus, else the name"
          " for this narrower term under the broader parent."),
        editable=True)

    def __str__(self):
        return str(self.name)
# end class RelatedTerm

class BibvidTerm(models.Model):
    id = models.AutoField(primary_key=True)

    bibvid = models.ForeignKey('Bibvid', null=False, on_delete=models.CASCADE,
      help_text =('The Bib_vid now using this term'
      'suggested terms'),
      )

    # Note, internally a unique suffix for the relation name
    # NOTE: it must be unique within the snow flake tree

    mets_element = SpaceCharField(max_length=255,
        unique=False, blank=False, null=False, default='name',
        help_text= ("METS element that contains this term."),
        editable=True)

    name = SpaceCharField(verbose_name='Related term name', max_length=255,
        unique=False, blank=False, null=False, default='name',
        help_text= ("If no parent, name of thesaurus, else the name"
          " for this narrower term under the broader parent."),
        editable=True)

    def __str__(self):
        return str(self.name)
# end class RelatedTerm

#  Todo: add a one-to-one model with Theseaurus with
#  to use to record the xml tag to use for each thesaurus.
#  This way limited access can be provided for that value
class Thesaurus(models.Model):
    '''
    Thesaurus- for each row here, a row may exist in ThesTree
    that represents the root of the tree of terms in the thesaurus.
    Note that a ThesTree row with no parent (Null parent value) is a thesaurus
    tree 'root'.

    To contain metadata on the thesaurus
    TODO - design and implement code to import to a thesaurus from a
    spreadsheet  like Suzanne's, and to export to a spreadsheet.

    TODO: Add validation that the root is only a ThesTree row with a
          null parent.
    '''
    id = models.AutoField(primary_key=True)
    root = models.ForeignKey('ThesTree', null=False,
        on_delete=models.CASCADE)

    def __str__(self):
        return str(self.root.name)
#end class Thesaurus

# TermSuggestion - each row represents a "GetSuggestedTerms"
# Response, and some associated request parameters
class TermSuggestion(models.Model):
    '''
    A row exists for every GetSuggestedTerm API response.
    '''
    id = models.AutoField(primary_key=True)

    # The Bib_vid whose content was used to in the request
    bibvid = models.ForeignKey('Bibvid', null=False, on_delete=models.CASCADE,
      help_text =('The Bib_vid whose content was used to request '
      'suggested terms'),
    )

    # Thesaurus is a row in thesauri with a name that is a 'location' name
    # known to Access Innovations GetSuggestedTerm API Request.
    # eg, 'floridathes', 'geofloridathes'
    # It was used in such a request to
    # elicit the response set of TermSuggestion terms
    thesaurus = models.ForeignKey('ThesTree', null=False,
      on_delete=models.CASCADE,
      help_text =('Thesaurus used for the "location" parameter in '
         'the GetSuggestedTerms API request to Access Innovations'),
      )

    retrieval_datetime = models.DateTimeField('Term search DateTime (UTC)',
        null=False, auto_now=True, editable=False)

    # Note: when saving a retrieval row: (1) the bibvid is analyzed and
    # (2) an API GetSuggestedTerms request is sent to AI and
    # (3) a row in relation apiterm is added for each api-returned term
    # (4) a note is made here about how processing of the bibvid to produce
    # the document that was sent with the AI API GetSuggestedTerm request
    # future;
    #
    # (*) also value count_pages might be autopopulated..
    # (*) also note may be populated with a desc of the logic of the retrieval
    # formulation (just jp2, just txt files used, maybe count of files etc)
    # (*) also the mets file is parsed if any, and metsterm rows are populated

    note = SpaceTextField(max_length=2550, null=True, default='note',
      blank=True, editable=True,)
    # Some value to consider adding here:
    # N  of pages, N of files of various types
    # time sent/received of api request/response
    # N of apiterms received
    #type of stratagy to produce text, eg if ocr even the tesseract or other
    #sofware version
    #Size in bytes of text document
    #Maybe allow stats per page sent, or one main retrieval for all text,
    #and a retrieval for each individual page... etc.. and on and on

    #Note on how the text content was extracted from the bibvid
    text_content_note = SpaceTextField(max_length=2550, null=True,
      default='note2', blank=True, editable=True,)

    # The optional filename in which is saved the content extracted from
    # this bibvid# and sent to Access Innovations that it used along with
    # the thesesaurus
    # (location) to provide its suggested terms response.

    content_save_file = SpaceTextField(max_length=25000, null=True,
      default='save', blank=True, editable=True, )

    def __str__(self):
        return str(self.bibvid.bibvid)


# end class TermSuggestion

'''
class TermEval
Evaluation of the aptness of the each for the bibvid of each TermSuggestion
'''
class TermEval(models.Model):
    id = models.AutoField(primary_key=True)
    response = models.ForeignKey('TermSuggestion', null=False,
        on_delete=models.CASCADE,
        help_text="GetSuggestedTerm API search which generated this term."
        )

    # name of the suggested term
    suggested_term = SpaceCharField(max_length=255, unique=True,
        default="Term name", editable=True)

    # The parent result's value for the 'count' of this suggested term.
    count_suggested = models.PositiveIntegerField(default=0,null=False)

    # A web site user edits this field to record the decision whether to
    # insert the  term as a subject into the item's METS file.
    approval_rating = models.PositiveIntegerField('Your Rating',
        default=50, null=False,
        help_text="If rated over 50, this term will be recorded in the METS."
        )

    def __str__(self):
        return str(self.suggested_term)

    ''' note: Do -not- set Meta.db_table
        Let Django do its thing
        and create the db table name via a prefix of the table
        class of app_name and _.
        It makes future migrations and many management operations much easier
        down the line.
        Changing it after doing some migrations will
        confuse migrations, too, which can be somewhat messy, or require
        a refresher review of migrations docs.

        class Meta:
          # Do NOT do this else django migrations get confused!
          # Just leave db_table unset.
          db_table = 'something'
    '''
#end class TermEval

# 20180926 - adding inspected tables, unmanaged, based on xml2rdb2 outputted
# tables from config xis_subjets.py.
# CAUTION: Reruns of that xml2rdb2 config, and its sql creates script will
# drop and repopulate these tables.

class X2018Thesis(models.Model):
    #orig:thesis = models.IntegerField(unique=True, blank=True, null=True)
    sn = models.IntegerField(primary_key=True)
    thesis = models.IntegerField(unique=True)
    uf_bibvid = models.CharField(max_length=16, blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    au_fname = models.CharField(max_length=40, blank=True, null=True)
    au_lname = models.CharField(max_length=40, blank=True, null=True)
    pub_year = models.CharField(max_length=16,blank=True, null=True)
    add_ymd = models.CharField(max_length=16,blank=True, null=True)
    add_initials = models.CharField(max_length=16,blank=True, null=True)
    change_ymd = models.CharField(max_length=16,blank=True, null=True)
    change_initials = models.CharField(max_length=16,blank=True, null=True)

    def __str__(self):
        return(self.uf_bibvid)

    class Meta:
        managed = False
        db_table = 'x2018_thesis'
        verbose_name_plural='x2018 theses'

class X2018Subject(models.Model):
    # Must declare thesis as primary_key to suppress auto 'id'
    # field that django creates
    sn = models.IntegerField(primary_key=True)
    thesis = models.ForeignKey(X2018Thesis,
      on_delete=models.CASCADE, db_index=True,
      db_column='thesis', blank=True, null=True)
    subject = models.IntegerField(blank=True, null=True)
    xtag = models.CharField(max_length=8, blank=True, null=True)
    term = SpaceCharField(max_length=100, blank=True, null=True)
    matches = models.IntegerField(blank=True, null=True)
    # Column 'source' is 'subject category source code': max 12 chars, per:
    # https://www.loc.gov/standards/sourcelist/subject.html
    source = models.CharField(max_length=12, blank=True, null=True)
    keep = models.CharField(max_length=1, blank=True, null=True)
    marc = models.CharField(max_length=3, blank=True, null=True)
    ind1 = models.CharField(max_length=1, blank=True, null=True)
    ind2 = models.CharField(max_length=1, blank=True, null=True)

    def __str__(self):
        # return(f"{self.thesis}.{self.subject}.{self.xtag}")
        # Only viewing these as inlines, and need no label there
        # return empty string. 'None' triggers an error.
        return ''

    class Meta:
        managed = False
        db_table = 'x2018_subject'
        unique_together = (('thesis', 'subject', 'xtag'),)

        #widgets to override
        #widgets = {'keep': forms.TextInput(attrs={'size':'1'})}
#end class X2018Subject
