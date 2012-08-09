import os
from decimal import Decimal
from django.db import models
from django.db.models.fields.files import FieldFile
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey

REGION_TYPES = (
    ('text', 'Text'),
    ('image', 'Image'),
)

ALIGN_CHOICES = (
    ('LEFT', 'Left'),
    ('CENTER', 'Center'),
    ('RIGHT', 'Right'),
    ('JUSTIFY', 'Justify'),
)

if not hasattr(settings, 'COMPDIR'):
    COMPDIR = os.path.join(settings.MEDIA_ROOT, 'impositions', 'comps')
else:
    COMPDIR = settings.COMPDIR
COMPSTORAGE = FileSystemStorage(location=COMPDIR)


class TemplateImage(models.Model):
    name = models.CharField(max_length=100)
    file = models.ImageField(upload_to='impositions/templates')

class DataLoader(models.Model):
    prefix = models.CharField(max_length=30)
    path = models.CharField(max_length=255)

    def __unicode__(self):
        from impositions.utils import get_data_loader
        DataLoader = get_data_loader(self.path)
        return DataLoader().verbose_name()

class Template(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField('Template file', upload_to='impositions/templates')
    fonts = models.CharField(max_length=255, blank=True)
    color_palette = models.CharField(max_length=255, blank=True)
    data_loaders = models.ManyToManyField(DataLoader, blank=True)

    def __unicode__(self):
        return self.name

    def get_color_palette(self):
        if self.color_palette:
            colors = self.color_palette.split(',')
            return [c.strip() for c in colors]
        return []

    def clean(self):
        from impositions import utils
        # make sure color values are valid
        if self.color_palette:
            palette = []
            for c in self.color_palette.split(','):
                try:
                    palette.append(utils.parse_color(c, True))
                except ValueError, e:
                    raise ValidationError(str(e))
            self.color_palette = ','.join(palette)

    def save(self):
        creating = not self.pk
        super(Template, self).save()
        if creating:
            default_loaders = getattr(settings, 'IMPOSITIONS_DEFAULT_DATA_LOADERS', [])
            for pfx in default_loaders:
                self.data_loaders.add(DataLoader.objects.get(prefix=pfx))

    def get_fonts(self):
        if self.fonts:
            fonts = self.fonts.split(',')
            return [f.strip() for f in fonts]
        return []

    def get_thumbnail(self):
        from impositions.utils import get_rendering_backend
        Backend = get_rendering_backend()
        backend = Backend()
        return backend.get_template_thumbnail(self.file.path)

    def get_dimensions(self):
        from impositions.utils import get_rendering_backend
        Backend = get_rendering_backend()
        backend = Backend()
        return backend.get_dimensions(self.file.path)

    @models.permalink
    def get_absolute_url(self):
        return ('impositions-template-edit', [self.pk])
        

class TemplateRegion(models.Model):
    template = models.ForeignKey(Template, related_name='regions')
    name = models.CharField(max_length=150, default='Unnamed Region')
    description = models.TextField(blank=True)
    content_type = models.CharField(max_length=16, choices=REGION_TYPES)
    top = models.IntegerField()
    left = models.IntegerField()
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    allowed_fonts = models.CharField(max_length=255,blank=True)
    allowed_font_sizes = models.CharField(max_length=50, blank=True)
    allowed_colors = models.CharField(max_length=255,blank=True)
    allowed_images = models.ManyToManyField(TemplateImage, blank=True)
    allow_markup = models.BooleanField()
    text_style = models.CharField(max_length=255, blank=True)
    text_align = models.CharField(max_length=20, choices=ALIGN_CHOICES, 
            blank=True, default='LEFT')
    crop = models.BooleanField()
    default_text = models.TextField('Default Text', blank=True)
    default_image = models.CharField('Default Image', max_length=255, blank=True)
    editable = models.BooleanField(default=True)

    class Meta:
        ordering = ['top', 'left']

    @property
    def size(self):
        return self.width, self.height

    @property
    def box(self):
        return (self.top, self.left, 
               self.top + self.height,
               self.left + self.width)

    def clean(self):
        from impositions import utils
        # make sure color values are valid
        if self.allowed_colors:
            colors = []
            for c in self.allowed_colors.split(','):
                try:
                    colors.append(utils.parse_color(c, True))
                except ValueError, e:
                    raise ValidationError(str(e))
            self.allowed_colors = ','.join(colors)

    def get_allowed_colors(self):
        if self.allowed_colors:
            allowed = self.allowed_colors.split(',')
            return [c.strip() for c in allowed]
        return []

    def get_allowed_fonts(self):
        if self.allowed_fonts:
            allowed = self.allowed_fonts.split(',')
            return [f.strip() for f in allowed]
        return []

    def get_allowed_font_sizes(self):
        from django.db.backends.util import format_number
        if self.allowed_font_sizes:
            allowed = self.allowed_font_sizes.split(',')
            return [Decimal(format_number(float(s),8,2)) for s in allowed]
        return []

    def __unicode__(self):
        return "{0} (Template: {1})".format(
            self.name,
            self.template.__unicode__()
        )

class Composition(models.Model):
    template = models.ForeignKey(Template)
    description = models.CharField(max_length=200)

    def __unicode__(self):
        return "[{0}] {1}".format(
            self.template.__unicode__(),
            self.description
        )

    def save(self):
        if not self.pk:
            # Automatically add regions for the newly created composition
            super(Composition, self).save()
            for region in self.template.regions.all():
                CompositionRegion(comp=self, template_region=region).save()
        else:
            super(Composition, self).save()
            
    def render(self, **kwargs):
        from impositions.utils import get_rendering_backend
        context = kwargs.pop('context', None)
        Backend = get_rendering_backend()
        backend = Backend(context=context)
        return backend.render(self, **kwargs)

    def get_context(self):
        context = {}
        for loader in self.template.data_loaders.all():
            from impositions.utils import get_data_loader
            data_loader = get_data_loader(loader.path)()
            try:
                source = self.data_sources.get(loader=loader)
                data_loader.set_instance(source.content_object)
            except CompositionDataSource.DoesNotExist:
                pass
            context.update(data_loader.get_context(loader.prefix))
        return context

    def load_default_data(self):
        for region in self.regions.all():
            region.load_default_data()
            region.save()

    def get_thumbnail(self, regions=None):
        from impositions.utils import get_rendering_backend
        Backend = get_rendering_backend()
        backend = Backend()
        return backend.get_thumbnail(self, regions=regions)

    def add_data_source(self, prefix, object):
        loader = DataLoader.objects.get(prefix=prefix)
        data_source = CompositionDataSource(loader=loader, content_object=object)
        self.data_sources.add(data_source)

    @models.permalink
    def get_absolute_url(self):
        return ('impositions-comp-edit', [self.pk])
        
class CompositionDataSource(models.Model):
    composition = models.ForeignKey(Composition, related_name='data_sources')
    loader = models.ForeignKey(DataLoader)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ['composition', 'loader']

class CompositionRegion(models.Model):
    comp = models.ForeignKey(Composition, related_name='regions')
    template_region = models.ForeignKey(TemplateRegion)
    image = models.ImageField(upload_to='impositions/assets', blank=True)
    text = models.TextField(blank=True)
    font = models.CharField(max_length=50, blank=True)
    font_size = models.DecimalField(max_digits=8, decimal_places=2, 
                                    null=True, blank=True)
    bg_color = models.CharField('Background', max_length=50, blank=True)
    fg_color = models.CharField('Color', max_length=50, blank=True)
    border_color = models.CharField(max_length=50, blank=True)
    border_size = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['template_region__top', 'template_region__left']

    def __unicode__(self):
        return self.template_region.name
    
    def load_default_data(self):
        from django import template
        context = self.comp.get_context()
        type = self.template_region.content_type
        if type == 'image':
            default_image = self.template_region.default_image
            if '.' in default_image:
                prefix, varname = default_image.split('.', 1)
                img = context.get(prefix, {}).get(varname, None)
            else:
                img = context.get(default_image, None)
            # if image is not a FieldFile, assume it's a file-like object
            if isinstance(img, FieldFile):
                self.image = img
            elif img is not None:
                self.image.save(os.path.basename(img.name), img, save=False)
        elif type == 'text':
            tpl = template.Template(self.template_region.default_text)
            default = tpl.render(template.Context(context)).strip()
            self.text = default

    def get_fg_color(self):
        from impositions import utils
        if self.fg_color:
            return self.fg_color
        allowed = self.template_region.get_allowed_colors()
        return len(allowed) > 0 and allowed[0] or utils.DEFAULT_COLORS[0]

    def get_bg_color(self):
        from impositions import utils
        if self.bg_color:
            return self.bg_color
        allowed = self.template_region.get_allowed_colors()
        return len(allowed) > 0 and allowed[0] or utils.DEFAULT_BG_COLORS[0]

    def get_font(self):
        from impositions import utils
        if self.font:
            return self.font
        allowed = self.template_region.get_allowed_fonts()
        return len(allowed) > 0 and allowed[0] or utils.DEFAULT_FONTS[0]

    def get_font_size(self):
        from impositions import utils
        if self.font_size:
            return self.font_size
        allowed = self.template_region.get_allowed_font_sizes()
        return len(allowed) > 0 and allowed[0] or utils.DEFAULT_FONT_SIZES[0]
