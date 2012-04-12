import StringIO
from django.core.exceptions import ValidationError

class BaseRenderingBackend(object):
    supported_formats = []

    def __init__(self, comp, context={}, output=None):
        self.comp = comp
        self.context = context
        self.output = output
        if self.output is None:
            self.output = StringIO.StringIO()
    
    def validate(self):
        for region in self.comp.regions.all():
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

    def render(self, fmt):
        raise NotImplementedError
