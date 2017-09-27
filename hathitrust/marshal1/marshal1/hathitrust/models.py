import uuid
from django.db import models
from django_enumfield import enum

# Create your models here.
class HathiItemState(enum.Enum):
       HAS_FOLDER = 0
       FOLDER_LOADED = 1
       FILES_EXAMINED = 2
       FILES_NEED_CHANGES = 3
       YAML_CREATED = 4

class Hathi_item(models.Model):
    id = models.UUIDField(Primary_key=True, default=uuid.uuid4, editable=False)
    folder_path = models.CharField()
    state_code = models.IntegerField()
    yaml_status = models.IntegerField()
