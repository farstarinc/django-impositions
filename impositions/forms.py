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
        
        to_choices = lambda l: [(v.strip(),v.strip()) for v in l]
        font_choices = to_choices(template.get_fonts())
        color_choices = to_choices(template.get_color_palette())
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

class CompositionForm(forms.ModelForm):
    model = models.Composition

class CompRegionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.composition_instance = kwargs.pop('composition_instance', None)

        super(CompRegionForm, self).__init__(*args, **kwargs)
        
        # don't deal w/ empty form
        if self.prefix.endswith('__prefix__'):
            return

        region = self.instance.template_region
       
        fonts = font_sizes = colors = None
        if region:
            # get allowed values
            fonts = region.get_allowed_fonts() or region.template.get_fonts() \
                    or utils.DEFAULT_FONTS
            font_sizes = region.get_allowed_font_sizes() or utils.DEFAULT_FONTS
            colors = region.get_allowed_colors() or region.template.get_color_palette() \
                    or utils.DEFAULT_COLORS

        to_choices = lambda l: [(v,v) for v in l]
        self.fields['font'] = forms.ChoiceField(choices=to_choices(fonts))
        self.fields['font_size'] = forms.ChoiceField(choices=to_choices(font_sizes))
        self.fields['fg_color'] = forms.ChoiceField(choices=to_choices(colors))

    model = models.CompositionRegion

class BaseCompRegionFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        self.max_num = instance.template.regions.count()
        super(BaseCompRegionFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, index, **kwargs):
        kwargs['composition_instance'] = self.instance
        return super(BaseCompRegionFormSet, self)._construct_form(index, **kwargs)

    def _get_empty_form(self, **kwargs):
        kwargs['composition_instance'] = self.instance
        return super(BaseCompRegionFormSet, self)._get_empty_form(**kwargs)
    empty_form = property(_get_empty_form)

CompositionRegionFormSet = inlineformset_factory(models.Composition,
                                                 models.CompositionRegion,
                                                 form=CompRegionForm,
                                                 formset=BaseCompRegionFormSet,
                                                 extra=0)
