import os
from decimal import Decimal
from django.db import models
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

    def get_thumbnail(self):
        from impositions.utils import get_rendering_backend
        Backend = get_rendering_backend()
        backend = Backend()
        template = self
        return backend.get_template_thumbnail(template)


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

    @property
    def size(self):
        return self.width, self.height

    @property
    def box(self):
        return (self.top, self.left, 
               self.top + self.height,
               self.left + self.width)
    
    def get_allowed_colors(self):
        from impositions import utils
        if self.allowed_colors:
            allowed = self.allowed_colors.split(',')
            return [utils.parse_color(c) for c in allowed]
        return []

    def get_allowed_fonts(self):
        if self.allowed_fonts:
            allowed = self.allowed_fonts.split(',')
            return [f.strip() for f in allowed]
        return []

    def get_allowed_font_sizes(self):
        if self.allowed_font_sizes:
            allowed = self.allowed_font_sizes.split(',')
            return [Decimal(s) for s in allowed]
        return []

    def __unicode__(self):
        return "{0} (Template: {1})".format(
            self.name,
            self.template.__unicode__()
        )

class Composition(models.Model):
    template = models.ForeignKey(Template)
    description = models.CharField(max_length=200)
    # TODO: add format property so user can choose format (jpg, png, pdf)

    def __unicode__(self):
        return "[{0}] {1}".format(
            self.template.__unicode__(),
            self.description
        )

    def render(self, fmt, **kwargs):
        from impositions.utils import get_rendering_backend
        Backend = get_rendering_backend()
        backend = Backend()
        return backend.render(self, fmt, **kwargs)

    def get_context(self, request):
        from impositions.utils import get_data_loader
        context = {}
        for source in self.data_sources.all():
            context.update(source.get_context(request))
            DataLoader = get_data_loader(self.loader.path)
            data_loader = DataLoader(request)
            data_loader.set_instance(self.content_object)
            context.update(data_loader.get_context(self.loader.prefix))
        return context
            
class CompositionDataSource(models.Model):
    composition = models.ForeignKey(Composition, related_name='data_sources')
    loader = models.ForeignKey(DataLoader)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

class CompositionRegion(models.Model):
    comp = models.ForeignKey(Composition, related_name='regions')
    template_region = models.ForeignKey(TemplateRegion)
    image = models.ImageField(upload_to='impositions/assets', blank=True)
    text = models.TextField(blank=True)
    font = models.CharField(max_length=50, blank=True)
    font_size = models.DecimalField(max_digits=8, decimal_places=2, 
                                    null=True, blank=True)
    bg_color = models.CharField(max_length=50, blank=True)
    fg_color = models.CharField(max_length=50, blank=True)
    border_color = models.CharField(max_length=50, blank=True)
    border_size = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.template_region.name

    def get_fg_color(self):
        from impositions import utils
        if self.fg_color:
            return utils.parse_color(self.fg_color)
        allowed = self.template_region.get_allowed_colors()
        return len(allowed) > 0 and allowed[0] or None

    def get_bg_color(self):
        from impositions import utils
        if self.bg_color:
            return utils.parse_color(self.bg_color)
        allowed = self.template_region.get_allowed_colors()
        return len(allowed) > 0 and allowed[0] or None

    def get_font(self):
        if self.font:
            return self.font
        allowed = self.template_region.get_allowed_fonts()
        return len(allowed) > 0 and allowed[0] or None

    def get_font_size(self):
        if self.font_size:
            return self.font_size
        allowed = self.template_region.get_allowed_font_sizes()
        return len(allowed) > 0 and allowed[0] or None
    
    def get_content(self, context):
        from django import template
        type = self.template_region.content_type
        if type == 'image':
            if self.image:
                return self.image.path
            if self.template_region.default_image:
                return context.get(self.template_region.default_image, None)
            return None
        elif type == 'text':
            tpl = template.Template(self.template_region.default_text)
            default = tpl.render(template.Context(context)).strip()
            return self.text.strip() or default
