from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from impositions import models
from impositions import utils

class CSVSelect(object):
    def value_from_datadict(self, data, files, name):
        return ','.join(data.getlist(name))

    def render(self, name, value, attrs):
        if value is None:
            value = []
        else:
            value = value.split(',')
        return super(CSVSelect, self).render(name, value, attrs)

class CSVSelectMultiple(CSVSelect, forms.SelectMultiple): pass
class CSVCheckboxSelectMultiple(CSVSelect, forms.CheckboxSelectMultiple): pass

class TemplateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TemplateForm, self).__init__(*args, **kwargs)
        choices = [(f,f) for f in utils.get_system_fonts()]
        self.fields['fonts'].widget = CSVSelectMultiple(choices=choices)
        color_help = 'Enter hex values (eg, #FF0000), separated by commas'
        self.fields['color_palette'].help_text = color_help
        self.fields['data_loaders'].help_text = ''

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
        self.fields['allowed_font_sizes'].help_text = 'Specify font sizes points, separated by comma'
       
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
        return super(BaseRegionFormSet, self)._construct_form(index, **kwargs)
    
    def _get_empty_form(self, **kwargs):
        kwargs['template_instance'] = self.instance
        return super(BaseRegionFormSet, self)._get_empty_form(**kwargs)
    empty_form = property(_get_empty_form)

TemplateRegionFormSet = inlineformset_factory(models.Template,
                                              models.TemplateRegion,
                                              form=RegionForm,
                                              formset=BaseRegionFormSet,
                                              extra=0)
