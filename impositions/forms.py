import re
from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from impositions import models
from impositions.utils import get_data_loader

class TemplateForm(forms.ModelForm):
    class Meta:
        model = models.Template
        widgets = {
            'data_loaders': forms.CheckboxSelectMultiple,
        }

class RegionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        template = kwargs.pop('template_instance', None)
        super(RegionForm, self).__init__(*args, **kwargs)
        if not template:
            return
        image_choices = self.get_field_choices(template, 'image')
        default_image = self.instance and self.instance.default_image or ''
        self.fields['default_image'].initial = default_image
        self.fields['default_image'].widget = forms.Select(choices=image_choices)

    def get_field_choices(self, template, type):
        choices = [('', '--------')]
        for loader in template.data_loaders.all():
            DataLoader = get_data_loader(loader.path)
            data_loader = DataLoader()
            field_choices = data_loader.get_field_choices('image', loader.prefix)
            choices.extend([(data_loader.verbose_name(), field_choices)])
        return choices

    def save(self, *args, **kwargs):
        key = 'default_image'
        if self.prefix:
            key = '{}-{}'.format(self.prefix, key)
        self.instance.default_value = self.data[key]
        super(RegionForm, self).save(*args, **kwargs)
                
    class Meta:
        model = models.TemplateRegion
        # these fields aren't used yet
        exclude = ['description', 'allowed_images', 'default_value']

class BaseRegionFormSet(BaseInlineFormSet):
    def _construct_form(self, index, **kwargs):
        kwargs['template_instance'] = self.instance
        return super(BaseInlineFormSet, self)._construct_form(index, **kwargs)

TemplateRegionFormSet = inlineformset_factory(models.Template,
                                              models.TemplateRegion,
                                              form=RegionForm,
                                              formset=BaseRegionFormSet,
                                              extra=0)
