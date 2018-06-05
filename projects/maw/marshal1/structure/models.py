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


# Create your models here.
class xrc_rel(models.Model):
    # hierarchical relation for an xrconfig output relation
    id = models.AutoField(primary_key=True)

    order = models.IntegerField(default=1,
     help_text="Relative order to output this xml tag within the parent tag.")

    xrconfig = models.ForeignKey('xrconfig', null=False, blank=False,
        on_delete=models.CASCADE,)

    # NOTE: a validation should be added to allow only ONE row per xrconfig
    # value to have a Null parent if manual edits are ever allowed.
    parent = models.ForeignKey('self', null=True, blank=True,
        on_delete=models.CASCADE,)

    min_occurs = models.IntegerField(null=False, default=True
      ,help_text="Minimum rows required with this parent.")

    max_occurs = models.IntegerField(null=False, default=True
      ,help_text="Maximum rows required with this parent.")

    name = SpaceCharField(max_length=255,
        unique=True, blank=False, null=False, default='',
        help_text="Unique name for this output relation for this xrconfig."
        , editable=True)

    xml_tag = SpaceCharField(max_length=255,
        unique=True, blank=False, null=False, default='',
        help_text="XML Tag name for one of the items in this relation."
        , editable=True)

    def __str__(self):
            return '{}:{}'.format(self.xrconfig, self.name)

    class Meta:
        unique_together = ('xrconfig', 'name')
        ordering = ['xrconfig', 'name', ]

class xrc_field(models.Model):
    # nodes for an xr config output field
    id = models.AutoField(primary_key=True)

    xrc_rel = models.ForeignKey('xrc_rel', null=False,
        blank=False,
        on_delete=models.CASCADE,)

    name = SpaceCharField(max_length=255,
        unique=True, blank=False, null=False, default='',
        help_text="Unique name for this field for this output relation."
        , editable=True)

    is_required = models.BooleanField(null=False, default=True
      ,help_text="True means a value is required.")

    default = SpaceCharField(max_length=255,
        unique=True, blank=False, null=False, default='',
        help_text="Default value for this field."
        , editable=True)

    # This field will be considered as an XML tag, else as an attribute.
    is_xml_tag = models.BooleanField(null=False, default=True
      ,help_text="True means the xml_name is an xml_tag. "
      "False for an attribute name.")

    xml_name = SpaceCharField(max_length=255,
        unique=True, blank=False, null=False, default='',
        help_text="XML tag or attribute name for this field."
        , editable=True)

    # Now the only type is string.. may want to adopt the types of fields
    # that django supports. In the meantime, just put notes in here, as the
    # value is not used yet...
    type = SpaceCharField(max_length=255,
        unique=True, blank=False, null=False, default='',
        help_text="Notes on editing and casting a value of this string field "
          "to a desired type",
        editable=True)

    def __str__(self):
            return '{}:{}.{}'.format(self.xrc_rel.xrconfig,
                self.xrc_rel, self.name)

    class Meta:
        unique_together = (('xrc_rel', 'name'))
        ordering = ['xrc_rel', 'name', ]

class xrc_ionode(models.Model):
    # xrc_ionode planned to represent a a map for an xml2rdb conversion
    # of an xml input file to an xrconfig set of relations
    # nodes for an xr config input/output map
    id = models.AutoField(primary_key=True)
    xrconfig = models.ForeignKey('xrconfig', null=False,
        blank=False,
        on_delete=models.CASCADE,)

    name = SpaceCharField(max_length=255,
        unique=True, blank=False, null=False, default='',
        help_text="Unique name for this xrconfig including version label ."
        , editable=True)
    pass
