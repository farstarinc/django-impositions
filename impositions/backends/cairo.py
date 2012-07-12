from __future__ import absolute_import
import os
import re
import cairo
import poppler
import pango
import pangocairo
from PIL import Image
from django.conf import settings
from impositions.backends import BaseRenderingBackend
from impositions import utils

try:
    from CStringIO import CStringIO as StringIO
except ImportError:
    from StringIO import StringIO

FONT_SCALE = .75 # no idea why, but we need this.

if not cairo.HAS_PDF_SURFACE:
    raise SystemExit('cairo was not compiled with PDF support')

class RenderingBackend(BaseRenderingBackend):
    supported_formats = ['pdf', 'png']
    
    def __init__(self, *args, **kwargs):
        super(RenderingBackend, self).__init__(*args, **kwargs)
        self.cr = None
        self.page = None
        self.pdf = None
        self.dpi = 300

    def setup_template(self, source_path, output=None):
        if self.cr and self.page and self.pdf:
            return

        # Get source document
        self.document = poppler.document_new_from_file('file://{}'.format(source_path), None)
        self.page = self.document.get_page(0)

        # Create destination document
        # TODO: There seems to be an issue with quality, possibly due to issues
        # with size calculations here.
        self.width, self.height = self.page.get_size()
        self.pdf = cairo.PDFSurface(output, self.width, self.height)
        self.cr = cairo.Context(self.pdf)
        
        # Set a white background
        self.cr.save()
        self.cr.set_source_rgb(1,1,1) # set white bg
        self.cr.paint()
        self.cr.restore()

        # Render source pdf to destination
        self.cr.save()
        # NOTE: This is a costly function, especially with large PDFs. Consider
        # using task queuing (eg, celery)
        self.page.render_for_printing(self.cr)
        self.cr.restore()

    def render_text_region(self, region):
        x, y = region.template_region.left, region.template_region.top
        self.cr.move_to(x, y)
        pc_context = pangocairo.CairoContext(self.cr)
        pc_context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        
        # setup pango layout
        layout = pc_context.create_layout()
        font_size = float(region.get_font_size()) * FONT_SCALE
        font_desc = '{} {}'.format(region.get_font(), font_size)
        font = pango.FontDescription(font_desc)
        layout.set_font_description(font)

        # if a width is given, set width and word wrap
        if region.template_region.width:
            layout.set_width(region.template_region.width * pango.SCALE)
            layout.set_wrap(pango.WRAP_WORD)

        content = region.text
        if not region.template_region.allow_markup:
            content = re.sub(r'<[^>]*?>', '', content)

        # construct surrounding span tag if any style attrs were given
        style = region.template_region.text_style
        if style:
            content = '<span {}>{}</span>'.format(style, content)
        
        if region.template_region.text_align == 'JUSTIFY':
            layout.set_justify(True)
        else:
            align = region.template_region.text_align or 'LEFT'
            layout.set_alignment(getattr(pango, 'ALIGN_{}'.format(align)))

        layout.set_markup(content)
        rgb = (0,0,0)
        color = region.get_fg_color()
        if color:
            rgb = utils.parse_color(color)
        self.cr.set_source_rgb(*[float(c)/255 for c in rgb])
        pc_context.update_layout(layout)
        pc_context.show_layout(layout)

    def get_png(self, fobj):
        output = StringIO()
        if isinstance(fobj, basestring):
            path = fobj
            if not path.startswith('/'):
                path = os.path.join(settings.MEDIA_ROOT, path)
            fobj = open(fobj)
        img = Image.open(fobj)
        img.save(output, format="PNG")
        output.seek(0)
        return output

    def render_image_region(self, region):
        if not region.image:
            return
        region_image = self.get_region_image(region)
        png = self.get_png(region_image)
        image = cairo.ImageSurface.create_from_png(png)

        x, y = region.template_region.left, region.template_region.top
        self.cr.translate(x, y)
        scale_factor = 72./self.dpi
        self.cr.scale(scale_factor, scale_factor)
        self.cr.set_source_surface(image)
        self.cr.paint()

    def render(self, comp, output=None, fmt=None, regions=None):
        self.validate(comp, regions)
        
        if not output:
            output = StringIO()

        if fmt == 'pdf':
            pdf_output = output
            self.dpi = 300
        else:
            pdf_output = None
            self.dpi = 72
        self.setup_template(comp.template.file.path, output=pdf_output)

        if regions is None:
            regions = comp.regions.all()

        for region in regions:
            self.cr.save()
            if region.template_region.content_type == 'text':
                self.render_text_region(region)
            elif region.template_region.content_type == 'image':
                self.render_image_region(region)
            self.cr.restore()
        
        # Finish
        if fmt is None:
            return self.pdf
        elif fmt == 'pdf':
            self.pdf.show_page()
            return pdf_output
        elif fmt == 'png':
            self.pdf.write_to_png(output)
        else:
            raise ValueError("Format not supported by cairo backend: {}".format(fmt))

        return output
        

    def get_thumbnail(self, comp, regions=None):
        dir = os.path.join('impositions', 'comps')
        full_dir = os.path.join(settings.MEDIA_ROOT, dir)
        filename = 'comp_{}_thumb.png'.format(comp.pk)
        path = os.path.join(full_dir, filename)
        if not os.path.exists(full_dir):
            os.makedirs(full_dir)
        file = open(path, 'w')
        self.render(comp, regions=regions)
        self.pdf.write_to_png(file)
        file.close()
        return os.path.join(dir, filename)

    def get_template_thumbnail(self, template_path):
        # Check for rendered thumb in media
        dir = os.path.join('impositions', 'templates')
        full_dir = os.path.join(settings.MEDIA_ROOT, dir)
        filename = '{}.png'.format(os.path.basename(template_path))
        path = os.path.join(full_dir, filename)
        if not os.path.exists(path):
            if not os.path.exists(full_dir):
                os.makedirs(full_dir)
            file = open(path, 'w')
            self.setup_template(template_path)
            self.pdf.write_to_png(file)
            file.close()
        return os.path.join(dir, filename)
