# file forms.py for MAW application 'submit' est 20180525
from .models import (
  Affiliation, Author, File,
  MaterialType, MetadataType,
  NoteType, ResourceType,
  Submittal, SubmittalAuthor, SubmittalFile
  )

from django.forms import TextInput, Textarea
from django.db import models
from maw_utils import ExportCvsMixin
from django.forms import inlineformset_factory

# see:
# https://stackoverflow.com/questions/14296350/include-a-form-for-a-related-object-in-a-modelform-in-django
#

class FileForm(forms.modelForm):
    class Meta:
        model = Author
        exclude = ()
    pass

class SubmittalForm(forms.ModelForm):
    ''' Edit a Submittal and its related data
    '''
    class Meta:
        model = Submittal
        exclude = ()

    def __init__(self, *args, **kwargs):
        #super(SubmittalForm, self).__init__(*args, **kwargs)
        super().__init__(*args, **kwargs)
        self.fields['file'].required = False
        data = kwargs.get('data')
        # ' prefix parameter required if in a modelFormset
        self.file_form = FileForm(instance=self.instance and self.instance.file,
            prefix=self.prefix, data=data)

    def clean(self):
        if not self.file_form.is_valid():
            raise forms.ValidationError("File not valid")

    def save(self,commit=True):
        obj = super(SubmittalForm, self).save(commit=commit)
        obj.file = self.house_form.save()
        obj.save()
# end class SubmittalForm
