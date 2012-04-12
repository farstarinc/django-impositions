from PIL import Image, ImageFont, ImageDraw, ImageOps
from . import BaseRenderingBackend

# TODO: add custom exceptions and error handling

class RenderingBackend(BaseRenderingBackend):

    base = None
    path = None
    fmt = None
    impositions = []

    def __init__(self, comp):
        self.comp = comp
        self.base = self.pilimg(comp.template.image.path)

    def impose_text(self, text, pos, font_path=None, color="black", size=12):
        if len(pos) > 2:
            pos = (pos[0], pos[1])
        # ^^^ if pos is a 4-tuple, just use the first 2, since we aren't going
        # ^^^ to crop or resize the text image to fit... we want it as-is
        textimg = self.create_text_image(text, font_path, color, size)
        self.base.paste(textimg, pos, textimg)
        self.impositions.append((textimg, pos))
        return self

    def impose_image(self, img, box, center=True):
        top = self.pilimg(img).convert('RGBA')
        top, box = self.fit_and_position(top, box, center)
        self.base.paste(top, box, top) # pass top as mask so transparency isn't pasted
        return self

    def save(self, fmt=None, path=None):
        if not path:
            path = self.path
        try:
            self.base.save(path, fmt)
        except:
            raise # need to think of good way to handle this error
        else:
            return self

    def fit_and_position(self, img, box, center=True):
        img = self.pilimg(img)
        boxw, boxh = self.boxsize(box)
        imw, imh = img.size

        if imw > boxw or imh > boxh:
            img = ImageOps.fit(img, (boxw, boxh), method=Image.ANTIALIAS,
                               centering=(0.5, 0.5)) # crop all sides equally
        else:
            if center:
                xpad = (boxw - imw) / 2
                ypad = (boxh - imh) / 2
                left = box[0] + xpad
                top = box[1] + ypad
            else:
                left = box[0]
                top = box[1]
            box = (left, top)

        return (img, box)

    def get_image_palette(self, maxcolors=100):
        img = self.base.convert('RGBA')
        colors = img.getcolors(img.size[0]*img.size[1])
        colors.sort(reverse=True)
        colors = filter(lambda x: x[1][3]>0, colors) # remove transparent colors
        rgba = colors[:maxcolors]
        rgb = map(lambda x: x[1][:3], rgba) # remove color count, already sorted
        # always add white and black
        if (255,255,255) not in rgb:
            rgb.append((255,255,255))
        if (0,0,0) not in rgb:
            rgb.append((0,0,0))
        rgb.sort() # not a great way to sort colors, but better than nothing
        return rgb

    def pilimg(self, img):
        if hasattr(img, '__module__') and img.__module__.startswith('PIL.'):
            return img
        else:
            return Image.open(img)

    def create_text_image(self, text, font_path, color, size):
        font = ImageFont.truetype(font_path, size*4)
        # ^^^ text drawn with PIL is choppy, so we're drawing the text large
        # ^^^ and resizing the resulting image
        dimensions = font.getsize(text)
        img = Image.new('RGBA', dimensions, (0,0,0,0))
        draw = ImageDraw.Draw(img)
        draw.text((0,0), text, font=font, fill=color)
        shrunk = (dimensions[0]/2, dimensions[1]/2)
        return img.resize(shrunk, Image.ANTIALIAS)

    def boxsize(self, box):
        w = box[2] - box[0]
        h = box[3] - box[1]
        return (w, h)
        
    def render(self, fmt='JPEG'):
        comp = self.comp
        output = engine.ImagingBackend(comp.template.image.path, COMPDIR)
        engine = import_module(imaging_module, package='impositions')

        for region in comp.regions.all():
            if region.region.content_type == 'text':
                output.impose_text(
                    region.fill.text,
                    region.region.box,
                    region.fill.font.font_file.path,
                    region.fill.fg_color,
                    region.fill.font_size
                )
            elif region.region.content_type == 'image':
                output.impose_image(region.fill.image.path, region.region.box)
            else:
                raise NotImplementedError

        filepath = "{0}/{1}_{2}.jpg".format(
            COMPDIR,
            comp.template.name,
            datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        )

        output.save(fmt, filepath)
        comp.file_path = filepath
        comp.save()
        return filepath
