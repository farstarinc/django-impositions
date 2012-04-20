from django import forms
from django.forms.models import inlineformset_factory
from impositions import models

class TemplateForm(forms.ModelForm):
    class Meta:
        model = models.Template
        widgets = {
            'data_loaders': forms.CheckboxSelectMultiple,
        }

class RegionForm(forms.ModelForm):
    class Meta:
        model = models.TemplateRegion
        # these fields aren't used yet
        exclude = ['description', 'allowed_images']

TemplateRegionFormSet = inlineformset_factory(models.Template,
                                              models.TemplateRegion,
                                              form=RegionForm,
                                              extra=0)
