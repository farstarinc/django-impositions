import itertools
from django.db.models.fields import FieldDoesNotExist

class BaseDataLoader(object):
    model = None
    fields = []
    
    def __init__(self):
        if not self.model:
            raise ValueError("model is required for data loaders")
        self.instance = None
    
    def set_instance(self, instance):
        self.instance = instance

    def verbose_name(self):
        model_name = self.model._meta.verbose_name
        return '{} Data'.format(model_name.title())

    def get_fields(self):
        return self.fields

    def get_field_value(self, field):
        func = getattr(self, field, None)
        if func and callable(func):
            return func()
        if not self.instance:
            return None
        try:
            return getattr(self.instance, field)
        except AttributeError:
            pass
        return None
    
    def get_field_verbose_name(self, field):
        try:
            field = self.model._meta.get_field(field)
            return unicode(field.verbose_name).capitalize()
        except FieldDoesNotExist:
            return None

    def get_field_choices(self, type, prefix):
        choices = []
        for field in self.fields[type]:
            key = '.'.join((prefix, field))
            verbose_name = self.get_field_verbose_name(field)
            if not verbose_name:
                func = getattr(self, field, None)
                if func and hasattr(func, 'verbose_name'):
                    verbose_name = func.verbose_name
            if not verbose_name:
                verbose_name = field.replace('_', ' ').capitalize()
            choices.append((key, verbose_name))
        return choices
        
    def get_context(self, prefix):
        context = {}
        fields = itertools.chain(*self.get_fields().values())
        for f in fields:
            value = self.get_field_value(f)
            context[f] =value
        if prefix:
            return {prefix: context}
        return context
 
