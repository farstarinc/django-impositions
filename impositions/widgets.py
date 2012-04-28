from django import forms
from django.utils.safestring import mark_safe
from easy_thumbnails.files import get_thumbnailer

def thumbnail(image_path, width, height, crop=True):
    thumbnail_options = dict(size=(width, height), crop=crop)
    thumbnail = get_thumbnailer(image_path).get_thumbnail(thumbnail_options)
    return u'<img src="%s" alt="%s" />' % (thumbnail.url, image_path)

class ImageWidget(forms.ClearableFileInput):
    template = '%(image)s<br />%(input)s'

    def __init__(self, attrs=None, template=None, width=200, height=200, crop=True):
        if template is not None:
            self.template = template
        self.width = width
        self.height = height
        self.crop = crop
        super(ImageWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        input_html = super(ImageWidget, self).render(name, value, attrs)
        if hasattr(value, 'width') and hasattr(value, 'height'):
            image_html = thumbnail(value.name, self.width, self.height, self.crop)
            output = self.template % {'input': input_html,
                                      'image': image_html}
        else:
            output = input_html
        return mark_safe(output)
