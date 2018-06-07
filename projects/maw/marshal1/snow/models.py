from django.db import models
import uuid
#from django_enumfield import enum

#other useful model imports at times (see django docs, tutorials):
import datetime
from django.utils import timezone
from maw_utils import SpaceTextField, SpaceCharField, PositiveIntegerField
import django.contrib.postgres.fields as pgfields
from collections import OrderedDict
from django.core.serializers.json import DjangoJSONEncoder
#import maw_utils

'''
NOTE: rather than have a separate file router.py to host SnowRouter, I just
put it here. Also see settings.py should include this python import dot-path
as one of the listed strings in the list setting for DATABASE_ROUTERS.

'''
# Maybe move the HathiRouter later, but for now keep here
#
class SnowRouter:
    '''
    A router to control all db ops on models in the snow Application.
    '''

    # app_label is really an app name. Here it is hathitrust.
    app_label = 'snow'

    # app_db is really a main settings.py DATABASES name, which is
    # more properly a 'connection' name
    app_db = 'snow_connection'

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

# } end class SnowRouter

class Genre(models.Model):
    # Each row represents a snowflake relational hierarchy.
    # where a snowflake relational concept is similar to a complete xml
    # schema definition (XSD).
    # More formally the connections among the relations/nodes
    # in a snowflake genre embodies a directed acyclic graph (DAG),
    # but "dag" does not sound as generic or familiar as "genre".
    #
    id = models.AutoField(primary_key=True)

    name = SpaceCharField(verbose_name='Genre name', max_length=255,
        unique=True, blank=False, null=False, default='',
        help_text="Unique name for this snowflake genre."
          " Please include a version label suffix like 'V1.0'.",
        editable=True)

    create_datetime = models.DateTimeField(help_text='Creation DateTime',
        null=True, auto_now=True, editable=False)

    notes = SpaceTextField(max_length=2550,
        unique=False, blank=True, null=True, default='',
        help_text="(1) Used for? (2) based on? "
          "Newlines are discarded, so use (1), (2), etc, labels for notes.",
        editable=True)

    def __str__(self):
            return '{}'.format(self.name)

class Relation(models.Model):
    # This relation is one node in the DAG of its snowflake's relations,
    # where a relation is a node or branching-off point and a parent is
    # a line that connects two nodes.
    # A relation corresponds roughly to an xml element in an xml schema.
    id = models.AutoField(primary_key=True)

    # The containing snowflake genre of this relation
    genre = models.ForeignKey('genre', null=False, blank=False,
        on_delete=models.CASCADE,)

    # Only one relation in a genra may have a null parent
    parent = models.ForeignKey('self', null=True, blank=True,
        on_delete=models.CASCADE,)

    # Note, internally a unique suffix for the relation name
    # NOTE: it must be unique within the Genra
    name = SpaceCharField(verbose_name='Relation name', max_length=255,
        unique=False, blank=False, null=False, default='',
        help_text="Unique name for this relation under this genre."
        , editable=True)

    local_name = SpaceCharField(max_length=255,
        unique=False, blank=False, null=False, default='',
        help_text="Unique name for this relation among those with the same "
          "parent. Eg, an xml element name for some uses."
        ,editable=True)

    # NOTE: a validation should be added to allow only ONE node per snowflake
    # value to have a Null parent if manual edits are ever allowed.
    # There must be one node with a null parent, the root.
    # Also a validation should ensure that there must be
    # no cycles linking relations in a snowflake

    min_occurs = PositiveIntegerField(null=False, default=1
      ,help_text="Minimum occurrences required under this parent.")

    max_occurs = models.IntegerField(null=False, default=0,
      help_text="Maximum occurrences required under this parent. "
          "0 or null means no limit.")

    notes = SpaceTextField(max_length=2550,
        unique=False, blank=True, null=True, default='',
        help_text="Notes on this relation.",
        editable=True)

    '''
    Note: do NOT include fields 'order' or 'xml_tag' in this relation.
    Such information belongs in a template object that renders snowflake
    data to xml, say, or json, etc.
    See relation or application template that manages output format templates
    where templates reference snowflakes and describe output formatting for
    a snowflake in an output style (xml, etc).

    xml_tag = SpaceCharField(max_length=255,
        unique=True, blank=False, null=False, defagenre='',
        help_text="XML Tag name for one of the items in this relation."
        , editable=True)

    order = models.IntegerField(default=1,
     help_text="Relative order to output this xml tag within the parent tag.")
    '''

    def __str__(self):
            return '{}:{}'.format(self.genre, self.name)

    class Meta:
        unique_together = ( 'parent', 'local_name')
        unique_together = ('genre', 'name')
        ordering = ['genre', 'id', ]


class Field(models.Model):
    # fields for a snowflake relation.
    # This is roughly parallel to an element in xml.
    id = models.AutoField(primary_key=True)

    # relation is roughly equivalent to the immediate parent element of this
    # field/element
    relation = models.ForeignKey('relation', null=False,
        blank=False,
        on_delete=models.CASCADE,)

    name = SpaceCharField(verbose_name='Field name',max_length=255,
        unique=False, blank=False, null=False, default='',
        help_text="Unique name for this field under this relation."
        , editable=True)

    max_length =  PositiveIntegerField(
        null=True, blank=True,
        default=255,
        help_text="Maximum number of characters in this field."
        , editable=True)

    default = SpaceCharField(max_length=255,
        unique=True, blank=True, null=True, default='',
        help_text="Default value for this field."
        , editable=True)

    ''' Do NOT include the following fields in relation 'field'.
    Such fields belong in a template definition to structure output style
    and options.

    order = IntegerField .... field order to output to csv file, etc.

    # This field will be considered as an XML tag, else as an attribute.
    is_xml_tag = models.BooleanField(null=False, default=True
      ,help_text="True means the xml_name is an xml_tag. "
      "False for an attribute name.")

    xml_name = SpaceCharField(max_length=255,
        unique=True, blank=False, null=False, default='',
        help_text="XML tag or attribute name for this field."
        , editable=True)
    '''

    def __str__(self):
            return '{}:{}.{}'.format(self.relation.genre,
                self.relation, self.name)

    class Meta:
        unique_together = (('relation', 'name'))
        ordering = ['relation', 'name', ]

class Restriction(models.Model):
    # restrictions on field values for a snowflake relation.
    # This is roughly parallel to an element in xml.
    # This is a placeholder relation, to consider for further work.

    id = models.AutoField(primary_key=True)

    name = SpaceCharField(max_length=255,
        unique=False, blank=False, null=False, default='',
        help_text="Unique name for this field for this output relation."
        , editable=True)

    field = models.ForeignKey('field', null=False,
        blank=False, on_delete=models.CASCADE,)

    notes = SpaceTextField(max_length=2550,
        unique=False, blank=True, null=True, default='',
        help_text="Notes on this instance.",
        editable=True)

    #add fields here to restrict valid values

    # To be implemented or experimented- if given, restrict input
    # values to the set of values for the value set name in some new table
    # named value perhaps, with fields set_name and value
    # Also may be used to compose drop down lists for
    # manual editing processes
    values_set_name = SpaceCharField(max_length=255,
        unique=True, blank=True, null=True,
        default=None,
        help_text="Name of a values_set with the related field's allowed "
          "values.")

    # todo: Might also add fields also like regular_expression, pattern,
    # and other xsd 'facets' also  that XSD
    # schemas use: https://www.w3schools.com/xml/schema_facets.asp

    def __str__(self):
        return '{} {}'.format(self.name)
