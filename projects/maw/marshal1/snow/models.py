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
from mptt.models import MPTTModel, TreeForeignKey
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

class Schema(models.Model):
    # Each row represents a snowflake relational hierarchy.
    # where a snowflake relational concept is similar to a complete xml
    # schema definition (XSD).
    # More formally the connections among the relations/nodes
    # in a snowflake schema embodies a directed acyclic graph (DAG),
    # but "dag" does not sound as generic or familiar as "schema".
    #
    id = models.AutoField(primary_key=True)

    name = SpaceCharField(verbose_name='Schema name', max_length=255,
        unique=True, blank=False, null=False, default='',
        help_text="Unique name for this snowflake schema."
          " Please include a version label suffix like 'V1.0'.",
        editable=True)

    create_datetime = models.DateTimeField(help_text='Creation DateTime',
        null=True, auto_now=True, editable=False)

    notes = SpaceTextField(max_length=2550,
        unique=False, blank=True, null=True, default='',
        help_text="(1) Used for? (2) based on? "
          "Newlines are discarded, so use (1), (2), etc, labels for notes.",
        editable=True)

    '''
        to test 20180612 after morning demo...
    SCHEMA_CHOICES = (
        ( 'PENDING' ,'Test Schema Relations Pending'),
        ( 'TESTING', 'Test Schema Relations Available'),
        ( 'RELEASED' ,'Schema Relations Available, Schema Archived'),
    )

    schema_status = models.CharField('Partner', null=True, default='Available',
        blank=True, max_length=50, choices=SCHEMA_CHOICES,
        help_text="Partner to verify or edit this item.")
    '''

    def __str__(self):
            return '{}'.format(self.name)

class Node(MPTTModel):
    # This relation is one node in the DAG of its snowflake's relations,
    # where a relation is a node or branching-off point and a parent is
    # a line that connects two nodes.
    #
    # A relation corresponds roughly to an xml element in an xml schema.
    id = models.AutoField(primary_key=True)

    # The containing snowflake schema of this relation
    schema = models.ForeignKey('schema', null=False, blank=False,
        # Note use default=0 to quell makemigrations holdups
        on_delete=models.CASCADE, default=0)

    # Only one relation in a schema a null parent
    parent = models.ForeignKey('self', null=True, blank=True,
      related_name='children', db_index=True,
      verbose_name = "Parent relation",
      on_delete=models.CASCADE,)

    # Note, internally a unique suffix for the relation name
    # NOTE: it must be unique within the Genra
    name = SpaceCharField(verbose_name='Relation name', max_length=255,
        unique=False, blank=False, null=False, default='',
        help_text="Unique name for this relation under this schema."
        , editable=True)

class Relation(models.Model):
    # This relation is one node in the DAG of its snowflake's relations,
    # where a relation is a node or branching-off point and a parent is
    # a line that connects two nodes.
    #
    # A relation corresponds roughly to an xml element in an xml schema.
    id = models.AutoField(primary_key=True)

    # The containing snowflake schema of this relation
    schema = models.ForeignKey('schema', null=False, blank=False,
        # Note use default=0 to quell makemigrations holdups
        on_delete=models.CASCADE, default=0)

    # Only one relation in a schema a null parent
    parent = models.ForeignKey('self', null=True, blank=True,
      verbose_name = "Parent relation",
      on_delete=models.CASCADE,)

    # Note, internally a unique suffix for the relation name
    # NOTE: it must be unique within the Genra
    name = SpaceCharField(verbose_name='Relation name', max_length=255,
        unique=False, blank=False, null=False, default='',
        help_text="Unique name for this relation under this schema."
        , editable=True)

    '''
    Deprecate local_name 20180611 - because this is not a schema
    feature, but this is a template feature,
    to produce an output name from this field

    local_name = SpaceCharField(max_length=255,
        unique=False, blank=False, null=False, default='',
        help_text="Unique name for this relation among those with the same "
          "parent. Eg, an xml element name for some uses."
        ,editable=True)
    '''

    # NOTE: a validation should be added to allow only ONE node per snowflake
    # value to have a Null parent if manual edits are ever allowed.
    # There must be one node with a null parent, the root.
    # Also a validation should ensure that there must be
    # no cycles linking relations in a snowflake

    min_occurs = PositiveIntegerField(null=False, default=0
      ,help_text="Minimum occurrences required under this parent.")

    max_occurs = models.IntegerField(null=False, default=0,
      help_text="Maximum occurrences required under this parent. "
          "0 or null here means unbounded.")

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
        unique=True, blank=False, null=False, defaschema='',
        help_text="XML Tag name for one of the items in this relation."
        , editable=True)

    order = models.IntegerField(default=1,
     help_text="Relative order to output this xml tag within the parent tag.")
    '''

    def __str__(self):
            return '{}:{}'.format(self.schema, self.name)

    class Meta:
        unique_together = ( 'parent', 'local_name')
        unique_together = ('schema', 'name')
        ordering = ['schema', 'id', ]


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
        help_text="Unique name for this field under this relation.",
        editable=True)

    max_length =  PositiveIntegerField(
        null=True, blank=True,
        default=255,
        help_text="Maximum number of characters in this field.",
        editable=True)

    is_required = models.BooleanField( editable=True, default=False,
        help_text="Whether this field is required for a schema instance.")
    # do not add any more fields to 'Field'. If they involve validation
    # or data type, add to new tables like 'restriction' or lookup, etc
    # that have a fkey back to a field and other info it needs
    # might be diff restrictions tables like restriction_int, restriction_rx,
    # restriction_lookup, etc
    # Both fields max_length and is_required also are true restrictions,
    # but they are so common that we cheat and add them here
    # Note: later also may implement table-level restrictions like
    # trestrict_composite_unique_key,trestrict_exist, etc

    # We can also add lookups for fkey restrictions, etc.
    # So, we can use lookup for authority fields..
    # May need many-many table to link schema fields with authority source field
    # lists, so if a 'lookup' value is this type, then a m-m lookup row may have
    # to be provided...

    ''' Note: Not too elegant to put default value field here,
    but DID put simple fields max_length is_required flag.
    Otherwise, restrictions, validations and default values can be put
    on a future 'restriction' or 'validation' table where each row can
    have an fkey to this field.
    Note: also a new relation_restriction table could be added to register
    inter-table constraints.

    Do NOT include the following fields in relation 'field'.
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
            return '{}:{}.{}'.format(self.relation.schema,
                self.relation, self.name)

    class Meta:
        unique_together = (('relation', 'name'))
        ordering = ['relation', 'name', ]

class Regex(models.Model):
    # Regular expresion restrictions on field values for a snowflake relation.
    # This is roughly parallel to an element in xml.
    # This is a placeholder relation, to consider for further work.

    id = models.AutoField(primary_key=True)

    name = SpaceCharField(max_length=255,
        unique=False, blank=False, null=False, default='',
        help_text="Unique name for this field for this output relation."
        , editable=True)

    field = models.ForeignKey('field', null=False,
        blank=False, on_delete=models.CASCADE,)

    regex = SpaceCharField(max_length=255,
        unique=False, blank=False, null=False, default='',
        help_text="Unique name for this field for this output relation."
        , editable=True)

    notice = SpaceTextField(max_length=2550,
        unique=False, blank=True, null=True, default='',
        help_text="Notice to explain a violation for this regex.",
        editable=True)

    notes = SpaceTextField(max_length=2550,
        unique=False, blank=True, null=True, default='',
        help_text="Notes on this instance.",
        editable=True)

    #add fields here to restrict valid values
    # todo: Might also add fields also like regular_expression, pattern,
    # and other xsd 'facets' also  that XSD
    # schemas use: https://www.w3schools.com/xml/schema_facets.asp

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name_plural = 'Regexes'


    pass

class Vocabulary(models.Model):
    id = models.AutoField(primary_key=True)

    name = SpaceCharField(max_length=255,
        unique=False, blank=False, null=False, default='',
        help_text="Unique name for this vocabulary with version suffix.")

    def __str__(self):
            return '{}'.format(self.name)

    class Meta:
        verbose_name_plural = 'Vocabularies'


class Word(models.Model):
    id = models.AutoField(primary_key=True)

    vocabulary = models.ForeignKey('vocabulary', null=False,
        blank=False, on_delete=models.CASCADE,)

    word = SpaceCharField(max_length=255,
        unique=False, blank=False, null=False, default='',
        help_text="A word in this vocabulary.")

    def __str__(self):
        return '{}'.format(self.word)

    class Meta:
        unique_together = (('vocabulary', 'word'),)
        ordering = [ 'word', ]

class Match(models.Model):
    # Match restriction for a field to match a regular expression

    id = models.AutoField(primary_key=True)

    name = SpaceCharField(max_length=255,
        unique=False, blank=False, null=False, default='',
        help_text="Unique name for this match."
        , editable=True)

    field = models.ForeignKey('field', null=False,
        blank=False, on_delete=models.CASCADE,)

    regex = models.ForeignKey('regex', null=False,
        blank=False, on_delete=models.CASCADE,)

    def __str__(self):
            return '{}'.format(self.name)

    class Meta:
        verbose_name_plural = 'Matches'

class Lookup(models.Model):
    # restrictions on field values for a snowflake relation.
    # This is roughly parallel to an element in xml.
    # This is a placeholder relation, to consider for further work.
    # This has a unique restriction of field, so one can have at
    # most one lookup. If needed, we can relax that later and
    # allow a field to have more than one lookup, which would mean
    # a different implementation in the editing setup.

    id = models.AutoField(primary_key=True)

    name = SpaceCharField(max_length=255,
        unique=False, blank=False, null=False, default='',
        help_text="Unique name for this lookup."
        , editable=True)

    field = models.ForeignKey('field', null=False,
        blank=False, on_delete=models.CASCADE,)

    vocabulary = models.ForeignKey('vocabulary', null=False,
        blank=False, on_delete=models.CASCADE,)
