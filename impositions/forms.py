from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from impositions import models
from impositions import utils

class CSVSelect(object):
    def value_from_datadict(self, data, files, name):
        return ','.join(data.getlist(name))

    def render(self, name, value, attrs):
        value = value.split(',')
        return super(CSVSelect, self).render(name, value, attrs)

class CSVSelectMultiple(CSVSelect, forms.SelectMultiple): pass
class CSVCheckboxSelectMultiple(CSVSelect, forms.CheckboxSelectMultiple): pass

class TemplateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TemplateForm, self).__init__(*args, **kwargs)
        choices = [(f,f) for f in utils.get_system_fonts()]
        self.fields['fonts'].widget = CSVSelectMultiple(choices=choices)

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
        
        to_choices = lambda s: [(v.strip(),v.strip()) for v in s.split(',')]
        font_choices = to_choices(template.fonts)
        color_choices = to_choices(template.color_palette)
        self.fields['allowed_fonts'].widget = CSVSelectMultiple(choices=font_choices)
        self.fields['allowed_colors'].widget = CSVSelectMultiple(choices=color_choices)
       
        yesno = ((True, 'Yes'), (False, 'No'))
        self.fields['allow_markup'].widget = forms.RadioSelect(choices=yesno)

    def get_field_choices(self, template, type):
        choices = [('', '--------')]
        for loader in template.data_loaders.all():
            DataLoader = utils.get_data_loader(loader.path)
            data_loader = DataLoader()
            field_choices = data_loader.get_field_choices('image', loader.prefix)
            choices.extend([(data_loader.verbose_name(), field_choices)])
        return choices

    class Meta:
        model = models.TemplateRegion
        # these fields aren't used yet
        exclude = ['description', 'allowed_images']


class BaseRegionFormSet(BaseInlineFormSet):
    def _construct_form(self, index, **kwargs):
        kwargs['template_instance'] = self.instance
        return super(BaseInlineFormSet, self)._construct_form(index, **kwargs)

TemplateRegionFormSet = inlineformset_factory(models.Template,
                                              models.TemplateRegion,
                                              form=RegionForm,
                                              formset=BaseRegionFormSet,
                                              extra=0)
