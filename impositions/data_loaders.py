import itertools

class BaseDataLoader(object):
    model = None
    fields = []
    
    def __init__(self, request=None):
        if not self.model:
            raise ValueError("model is required for data loaders")
        self.request = request
        self.instance = None
    
    def set_instance(self, instance):
        self.instance = instance

    def verbose_name(self):
        model_name = self.model._meta.verbose_name
        return '{} Data'.format(model_name.title())

    def get_fields(self):
        return self.fields

    def get_field_value(self, field):
        if not self.instance:
            return None
        try:
            getattr(self.instance, field)
        except AttributeError:
            pass
        func = getattr(self, field, None)
        if func and callable(func):
            return func()
        return None

    def get_context(self, prefix):
        context = {}
        fields = itertools.chain(v for k,v in self.get_fields())
        for f in fields:
            if prefix:
                f = '.'.join(prefix, f)
            context[f] = self.get_field_value(f)
        return context
