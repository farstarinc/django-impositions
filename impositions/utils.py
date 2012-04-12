import re
from django.utils.importlib import import_module
from django.conf import settings

def get_rendering_backend():
    imaging_module = '.backends.{0}'.format(settings.IMPOSITIONS_BACKEND)
    engine = import_module(imaging_module, package='impositions')
    return engine.RenderingBackend

def parse_color(color):
    if isinstance(color, basestring):
        color = color.strip()
        # Check for css hex format
        re_hex = re.compile('^#?(([a-fA-F0-9]){3}){1,2}$')
        if re_hex.match(color):
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

