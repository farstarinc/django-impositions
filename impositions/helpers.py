import django
from django.forms.models import inlineformset_factory

class InlineFormSetMixin(object):
    """
    Allows addition of a single inline formset to a ModelForm
    """
    formset_class = None
    formset_model = None

    def __init__(self, *args, **kwargs):
        if not self.formset_class:
            self.formset_class = inlineformset_factory(self.model,
                    self.formset_model)
        super(InlineFormSetMixin, self).__init__(*args, **kwargs)
    
    def get_formset_class(self):
        return self.formset_class
    
    def get_formset(self, formset_class):
        return formset_class(**self.get_formset_kwargs())
    
    def get_formset_kwargs(self):
        kwargs = {'instance': self.object}
        if django.VERSION >= (1,4):
            kwargs['initial'] = self.get_initial()
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_formset_initial(self):
        """
        Returns a list of initial-data dicts to use for the formet's initial data
        """
        return []

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        formset_class = self.get_formset_class()
        form = self.get_form(form_class)
        formset = self.get_formset(formset_class)
        context = self.get_context_data(form=form, formset=formset)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        formset_class = self.get_formset_class()
        form = self.get_form(form_class)
        formset = self.get_formset(formset_class)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        self.object = form.save()
        formset.instance = self.object
        formset.save()
        return super(InlineFormSetMixin, self).form_valid(form)

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

