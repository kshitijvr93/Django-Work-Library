import uuid
from django.db import models

# Create your models here.

class Hathi_item(models.Model):
    id = models.UUIDField(Primary_key=True, default=uuid.uuid4, editable=False)
    folder_path = models.CharField()
    state_code = models.IntegerField()
