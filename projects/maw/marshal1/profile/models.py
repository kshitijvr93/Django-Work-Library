import uuid
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

import datetime
from django.utils import timezone
from maw_utils import SpaceTextField, SpaceCharField, PositiveIntegerField

class CubaLibro(models.Model):
    id = models.AutoField(primary_key=True)
    # Note: Django gives hint that OneToOne field usually is
    # better than a unique ForeignKey, as we use here for field
    # 'user', but in the case of models in app 'profile',, we
    # anticipate many such models in this 'profile' app to have
    # this type of relationship with the User table, where
    # same field names would collide, if using a OneToOne field,
    # so this way seems better.
    user = models.ForeignKey(User, unique=True, null=False
      , on_delete=models.CASCADE)

    # May add model later, but for now use same field def as
    # used in cuba_libro_item.agent -
    # TODO: promote this to django settings later
    # to conform to DRY principle and reference here and in cuba_libro

    PARTNER_CHOICES = (
        ( '-','-'),
        ( 'DUKE', 'Duke University'),
        ( 'FIU', 'Florida International'),
        ( 'HVD','Harvard'),
        ( 'NYP', 'New York Public'),
        ( 'UF' ,'University of Florida'),
        ( 'UMI' ,'University of Miami'),
        ( 'UNC','U of North Carolina'),
    )

    agent = models.CharField('Partner', null=False, default='UF',
        blank=True, max_length=50, choices=PARTNER_CHOICES,
        help_text="Partner who can claim to verify or edit this item.")

    note = SpaceTextField(blank=False, null=False,
        default="Your note here.",
        help_text="Optional note." )

    def __str__(self):
            return '{}'.format(self.agent)

#end class cuba_libro
