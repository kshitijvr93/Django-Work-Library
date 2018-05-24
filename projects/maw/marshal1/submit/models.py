import uuid
from django.db import models
#from django_enumfield import enum

#other useful model imports at times (see django docs, tutorials):
import datetime
from django.utils import timezone
from maw_utils import SpaceTextField, SpaceCharField

'''
NOTE: rather than have a separate file router.py to host HathiRouter, I just
put it here. Also see settings.py should include this python import dot-path
as one of the listed strings in the list setting for DATABASE_ROUTERS.

'''
# Maybe move the HathiRouter later, but for now keep here
#
class SubmitRouter:
    '''
    A router to control all db ops on models in the hathitrust Application.
    '''

    # app_label is really an app name. Here it is hathitrust.
    app_label = 'submit'

    # app_db is really a main settings.py DATABASES name, which is
    # more properly a 'connection' name
    app_db = 'submit_connection'

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

# } end class SubmitRouter

# { Start class MaterialType
class MaterialType(models.Model):
    id = models.AutoField(primary_key=True)
    name = SpaceCharField(max_length=255,
        unique=False, blank=True, null=True, default='',
        help_text="Unique name for a material type.", editable=True)
    description = SpaceTextField(blank=False, null=False,
        default="Your description here.",
        help_text="Description for this type of material." )
    '''
    Example names:
        'Conference Paper',
        'Conference Poster',
        'Conference Presentation',
        'Conference Procedings',
        'Journal Article',
        'Training Materials',
        'Pre-published Manuscript',
        'Pre-published Article',
        'Data Sets',
        'Student Organization Files',
        'Administrative Papers (Agendas, minutes, etc.)',
    '''
# } end class MaterialType

class ResourceType(models.Model):
    id = models.AutoField(primary_key=True)
    name = SpaceCharField(max_length=255, unique=True,
        blank=False, null=False, default='',
        help_text="Unique name for a resource type or format, per Catalogging.",
        editable=True)
    description = SpaceTextField(blank=False, null=False,
        default="Your description here.",
        help_text="Description for this type of resource." )
    '''
    Example names:
        'Photographs',
        'Video',
        'Audio file',
        'Text',
        'Conference Procedings',
        'Presentation/slides',
        'Data Sets',
        'Student Organization Files',
        'Administrative Papers (Agendas, minutes, etc.)',
    '''
# end class MetadataType
class MetadataType(models.Model):
    id = models.AutoField(primary_key=True)
    name = SpaceCharField(max_length=255, unique=True,
        blank=False, null=False, default='',
        help_text="Unique name for a Metadata or template type.", editable=True)
    description = SpaceTextField(blank=False, null=False,
        default="Your description here.",
        help_text="Description for this format of metadata." )
    '''
    Example metadata names may vary, as there may be more or fewer of
    those than material types. But some could be the same as some material
    type names, I suppose.

    Example sample here are just sample material types
        'Conference Paper',
        'Conference Poster',
        'Conference Presentation',
        'Conference Procedings',
        'Journal Article',
        'Training Materials',
        'Pre-published Manuscripts',
        'Pre-published Articles',
        'Data Sets',
        'Student Organization Files',
        'Administrative Papers (Agendas, minutes, etc.)',
    '''
# end class MetadataType


# { start class SubmittalNote
class NoteType(models.Model):
    id = models.AutoField(primary_key=True)
    note_type = SpaceCharField(max_length=50,
      blank=False, null=False, default='',
      unique=True,
      help_text="Brief words to (up to 50 characters) to name note type"
      )
    note_description = SpaceTextField(blank=False, null=False, default='',
      help_text="Description for this type of note up to 500 characters"
      )
# } end class SubmittalNote}


# { start class Submittal
class Submittal(models.Model):
    # Field 'id' is 'special', and if not defined here, Django defines
    # it as I do below anyway.
    # However I do include it per python Zen:
    # explicit is better than implicit.
    id = models.AutoField(primary_key=True)

    # See relation SubmittalAuthor for authorship, author ordering,
    # copyright license info for this submittal

    title_primary = SpaceTextField(max_length=255,null=True,
      default='', blank=True, editable=True,
      help_text="Title of the item you are submitting")
    submittal_datetime = models.DateTimeField(help_text='Submittal DateTime',
        null=False, auto_now=True, editable=False)

    material_type = models.ForeignKey('MaterialType',
        on_delete=models.CASCADE,)

    resource_type = models.ForeignKey('ResourceType',
        on_delete=models.CASCADE,)

    metadata_type = models.ForeignKey('MetadataType',
        on_delete=models.CASCADE,)
    # This will be automatically assigned in production
    bibid = SpaceCharField(max_length=255,  editable=True, blank=True, null=True,
        help_text = "This will be automatically assigned in production"
        )
    publisher = SpaceCharField(max_length=255, editable=True, blank=True,
        help_text = "This will be automatically assigned in production"
        )
    publication_date = models.DateField(blank=True, null=True,
      help_text='Date of publication.'
      )
    abstract = SpaceTextField(max_length=255,
      blank=False, null=False, default='',
      help_text='Abstract or summary of the content'
      )

    language = SpaceCharField(max_length=255,null=True, default='',blank=True,
      editable=True,
      help_text="The actual language.")

    def __str__(self):
        return str(self.title_primary)

    ''' WARNING FOR POSTERITY:
        Do -not- set db_table. Let Django do its thing
        and create the db table name via a prefix of the table
        class of AppConfig.name (see apps.py) and _.

        It makes future migrations and many management operations much easier
        down the line.

        Changing it after doing some migrations will
        confuse migrations, too, which can be very messy, and probably require
        substantial time for a refresher course in Django migrations.

        class Meta:
          db_table = 'item'
    '''
# } end class Submittal


#{ start class SubmittalNote
class SubmittalNote(models.Model):
    id = models.AutoField(primary_key=True)

    submittal_id = models.ForeignKey('Submittal',
        on_delete=models.CASCADE,
        help_text='Id of Submittal authored by this author',
        )

    note_type = models.ForeignKey('NoteType',
        on_delete=models.CASCADE,)

    note = SpaceTextField(max_length=255,null=True, default='',blank=True,
      editable=True,
      help_text="Your actual note text.")

# } end class SubmittalNote

#{ start class Author}
class Author(models.Model):
    id = models.AutoField(primary_key=True)

    orcid_id = SpaceTextField(max_length=255,null=True, default='',
        blank=True,editable=True,
        help_text="Orcid ID for this author"
        )

    email_address = models.EmailField()

    surname = SpaceCharField( help_text="Also known as last name or family name)",
        blank=False, null=False, default='',
        max_length=255, editable=True)

    given_name = SpaceCharField( help_text="Also known as first name)",
        blank=True, null=True, max_length=255, editable=True)

    create_date = models.DateTimeField(help_text='Author Insertion DateTime',
        null=True, auto_now=True, editable=False)

    ufdc_user_info = SpaceTextField(max_length=255,null=True, default='',
        blank=True, editable=True,help_text='UFDC user id info')

# } end class Author


# { Start class submittal author}
class SubmittalAuthor(models.Model):
    id = models.AutoField(primary_key=True)

    submittal_id = models.ForeignKey('Submittal', on_delete=models.CASCADE,
        help_text='Submittal authored by this author', )

    author_id = models.ForeignKey('Author', on_delete=models.CASCADE,
        help_text='Author of the associated submittal', )
    # May add affiliatin id here too.. to indicate the author's
    # institutional affiliation(s) to record for this submittal

# } end class SubmittalAuthor


'''
See https://fairuse.stanford.edu/overview/faqs/copyright-ownership/
May advise submitter to only submit items of which they are an author
and have not assigned-away their copyright to a publisher or another.

Also advise submitter to only submit items the whole of which they are
authors. For example, if they wrote only a chapter of a book, they are advised
to submit only the chapter, as they only have a right to issue a copyright
license for that chapter, not the whole book.

Also, advise them that they should list joint authors of the submittal, or
copyright assignees if they can, as they also may have active rights of
copyright and of credit for the work.

Also, ask the author(s) for assignment of the copyright to UF or even a
special license of their own design or agree to one from a multiple choice
list we provide, so that UF may copy, redistribute, etc.

Copyright law provides for any author to change the licensing statement(s)
over time, and even offer different licensing to different individuals or
segments of the public, etc.

So we may want to keep track of historical copyright licenses by date issued.
Also if there are multiple authors, multiple copyright licenses (at least one per
author per time span are possible.)

We should inform all authors for whom we have email addresses that their work
is provided in our repository and that they have the right to register their own
copyright license for the work at any time.
Each work should list asignees of copyrights, not just the author.
If the author assigns copyright to any other, we should record it and the contact
info so the public may ask permission of the assignee if wanted.


'''

# If an author assigns copyright to another, UF may want to provide that
# assignee an interface to add new licenses.
#

# { class SubmittalLicensor
# A lcensor is assumed to be valie and could be an author or
# another who was assigned or authorized by author to grant licenses.
# UF does no validation of thelegal standing of the indicated Licensor,
# so user must beware of validity of listed licensor to grant licenes.
#class SubmittalLicensor(models.Model):
    # id
    # submittal_id
    # licensor_id
    # assignor_id -- source SubmittalLicensor that added this row, and
    # value is either Null (if original author) or a Licensor of the
    # same submittal id (2-part composite key on submittal_id and licensor_id
    # that refers to another row in this table) active at the create_datetime
    # of this
    # row
    # if the assignment also rescinded author rights, the end_datetime is
    # populated, meaning that licensor not valid after that end_datetime.
    # None if this assignee is one of the original authors...
    #
    # start_datetime - dateime this Licensor was assigned
    #
    # author_rank - for referencing, crediting..
#End class


class File(models.Model):
    id = models.AutoField(primary_key=True)
    solitary_download_name = SpaceTextField(max_length=255,
        help_text="Name for a solitary downloaded file",
        blank=True, null=True, default='',
        editable=True)
    submittal_download_name = SpaceTextField(max_length=255,
        help_text="Name for a downloaded file within a submittal package",
        default='',
        blank=True, null=True, editable=True)

#end class Hathi_item
