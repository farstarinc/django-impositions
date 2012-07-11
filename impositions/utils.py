import re
import itertools
from decimal import Decimal
from django.utils.importlib import import_module
from django.conf import settings
from django.db.backends.util import format_number

DEFAULT_FONTS = ['Arial', 'Times New Roman']
DEFAULT_COLORS = ['#000000']
DEFAULT_BG_COLORS = ['#FFFFFF']
DEFAULT_FONT_SIZES = [Decimal(format_number(n,8,2))  for n in list(itertools.chain(
    range(8,17),
    range(18,29,2),
    range(32,49,4),
    range(54,73,6),
    range(80,100,8)
))]

class DataLoaderNotFound(Exception): pass

def get_rendering_backend():
    imaging_module = '.backends.{0}'.format(settings.IMPOSITIONS_BACKEND)
    engine = import_module(imaging_module, package='impositions')
    return engine.RenderingBackend

def get_data_loader(path):
    module, classname = path.rsplit('.', 1)
    mod = import_module(module)
    return getattr(mod, classname)

def parse_color(color, return_hex=False):
    if return_hex:
        return rgb2hex(*parse_color(color))

    if isinstance(color, basestring):
        color = color.strip()
        # Check for css hex format
        re_hex = re.compile('^#?(([a-fA-F0-9]){3}){1,2}$')
        if re_hex.match(color):
            if color.startswith('#'):
                color = color[1:]
            if len(color) == 3:
                color = ''.join(s*2 for s in color)
            if len(color) != 6:
                raise ValueError, "color #%s is not in #RRGGBB format" % color
            r, g, b = color[:2], color[2:4], color[4:]
            r, g, b = [int(n, 16) for n in (r, g, b)]
            return (r, g, b)
    try:
        if len(tuple) == 3 and all(isinstance(c, int) for c in color):
            return color
    except TypeError:
        pass

    raise ValueError("Unrecognized color: {}".format(color))

def rgb2hex(r, g, b):
    return '#{0:02X}{1:02X}{2:02X}'.format(r, g, b)

def get_system_fonts():
    # Currently this only works with the cairo backend
    if settings.IMPOSITIONS_BACKEND != 'cairo':
        raise NotImplementedError("Font listing does not work with the selected impositions backend.")
    import pangocairo
    font_map = pangocairo.cairo_font_map_get_default()
    font_list = [f.get_name() for f in font_map.list_families()]
    font_list.sort()
    return font_list
