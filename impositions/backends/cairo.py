from __future__ import absolute_import
import os
import re
import cairo
import poppler
import pango
import pangocairo
from django.conf import settings
from impositions.backends import BaseRenderingBackend
from impositions import utils

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

    def setup_template(self, source_path):
        if self.cr and self.page and self.pdf:
            return

        # Get source document
        self.document = poppler.document_new_from_file('file://{}'.format(source_path), None)
        self.page = self.document.get_page(0)

        # Create destination document
        self.width, self.height = self.page.get_size()
        self.pdf = cairo.PDFSurface(None, self.width, self.height)
        self.cr = cairo.Context(self.pdf)
        
        # Set a white background
        self.cr.save()
        self.cr.set_source_rgb(255,255,255) # set white bg
        self.cr.paint()
        self.cr.restore()

        # Render source pdf to destination
        self.cr.save()
        self.page.render(self.cr)
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
        self.cr.set_source_rgb(*[int(c) for c in rgb])
        pc_context.update_layout(layout)
        pc_context.show_layout(layout)

    def render_image_region(self, region):
        tpl_region = region.template_region
        if not region.image:
            return
        img_src = region.image.path
        image = cairo.ImageSurface.create_from_png(img_src)

        img_height = image.get_height()
        img_width = image.get_width()
        w = tpl_region.width
        h = tpl_region.height
        x, y = region.template_region.left, region.template_region.top
        self.cr.translate(x, y)
        width_ratio = float(w) / float(img_width)
        height_ratio = float(h) / float(img_height)
        if tpl_region.crop:
            scale_xy = min(height_ratio, width_ratio)
        else:
            scale_xy = max(height_ratio, width_ratio)
        self.cr.scale(scale_xy, scale_xy)
        self.cr.set_source_surface(image)
        self.cr.paint()

    def render(self, comp, fmt=None, regions=None):
        self.validate(comp, regions)
        self.setup_template(comp.template.file.path)

        if regions is None:
            regions = comp.regions.all()

        for region in regions:
            self.cr.save()
            if region.template_region.content_type == 'text':
                self.render_text_region(region)
            #elif region.template_region.content_type == 'image':
            #    self.render_image_region(region)
            self.cr.restore()
        
        # Finish
        if fmt is None:
            return
        elif fmt == 'pdf':
            self.pdf.show_page()
        elif fmt == 'png':
            self.pdf.write_to_png(self.output)
        else:
            raise ValueError("Format not supported by cairo backend: {}".format(fmt))
        
        # seek to beginning so that file object can be read
        self.output.seek(0)
        return self.output

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
