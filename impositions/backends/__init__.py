import os
from django.core.exceptions import ValidationError
from django.core.files import File
from easy_thumbnails.files import get_thumbnailer

class BaseRenderingBackend(object):
    supported_formats = []

    def __init__(self, context={}):
        self.context = context
        self.regions = []
        self.dpi = 72
    
    def validate(self, comp, regions=None):
        if regions is None:
            regions = comp.regions.all()

        for region in regions:
            name = region.template_region.name
            # check colors
            allowed = region.template_region.get_allowed_colors()
            fg_color = region.get_fg_color()
            bg_color = region.get_bg_color()
            if allowed and fg_color and fg_color not in allowed:
                raise ValidationError("Color not allowed in '{}': {}".format(name, fg_color))
            if allowed and bg_color and bg_color not in allowed:
                raise ValidationError("Color not allowed in '{}': {}".format(name, bg_color))

            # check font
            allowed = region.template_region.get_allowed_fonts()
            allowed = [f.strip().lower() for f in allowed]
            font = region.get_font()
            if allowed and font and font.lower() not in allowed:
                raise ValidationError("Font not allowed in '{}': {}".format(name, font))

    def get_region_image(self, region):
        """
        Returns a thumbnailed image according to region specs
        """
        # Save the file, in case it's an InMemoryUploadedFile
        tpl_region = region.template_region
        scale = self.dpi / 72
        size = tpl_region.width * scale, tpl_region.height * scale
        crop = tpl_region.crop and 'smart' or False
        thumbnail_opts = dict(size=size, crop=crop, upscale=True)
        imgfile = File(region.image.file)
        filename = os.path.basename(region.image.file.name)
        relative_name = os.path.join('impositions', 'thumbs', filename)
        thumbnailer = get_thumbnailer(imgfile, relative_name=relative_name)
        thumbnail = thumbnailer.get_thumbnail(thumbnail_opts)
        return thumbnail.path
    
    def set_context(self, context):
        self.context = context

    def render(self, comp, output=None, fmt=None, regions=None):
        raise NotImplementedError

    def get_thumbnail(self, comp):
        """
        Returns thumbnail for rendered comp for use with easy_thumbnails
        """
        raise NotImplementedError

    def get_template_thumbnail(self, template):
        """
        Returns thumbnail for rendered comp for use with easy_thumbnails
        """
        raise NotImplementedError
