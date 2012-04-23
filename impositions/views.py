from django.views.generic import list, edit
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.decorators import method_decorator
from django.forms.models import inlineformset_factory
from impositions import models, forms, utils

class TemplateBase(object):
    @method_decorator(permission_required('impositions.change_template'))
    def dispatch(self, request, *args, **kwargs):
        return super(TemplateBase, self).dispatch(request, *args, **kwargs)

class FormSetMixin(object):
    """
    Note that this cannot be used in a CreateView
    """
    formset_class = None
    formset_model = None

    def __init__(self, *args, **kwargs):
        if not self.formset_class:
            self.formset_class = inlineformset_factory(self.model,
                    self.formset_model)
        super(FormSetMixin, self).__init__(*args, **kwargs)
    
    def get_formset_class(self):
        return self.formset_class
    
    def get_formset(self, formset_class):
        return formset_class(**self.get_formset_kwargs())
    
    def get_formset_kwargs(self):
        kwargs = {'instance':self.object}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

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
        return super(FormSetMixin, self).form_valid(form)

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))


class TemplateListView(TemplateBase, list.ListView):
    model = models.Template
    context_object_name = 'templates'

class TemplateCreateView(TemplateBase, edit.CreateView):
    model = models.Template
    context_object_name = 'template'
    form_class = forms.TemplateForm

class TemplateUpdateView(TemplateBase, FormSetMixin, edit.UpdateView):
    model = models.Template
    context_object_name = 'template'
    form_class = forms.TemplateForm
    formset_class = forms.TemplateRegionFormSet
    success_url = '.'

    def form_valid(self, form, formset):
        response = super(TemplateUpdateView, self).form_valid(form, formset)
        msg = 'Template successfully saved.'
        messages.add_message(self.request, messages.SUCCESS, msg)
        return response

    def get_context_data(self, **kwargs):
        context = super(TemplateUpdateView, self).get_context_data(**kwargs)

        context['formset_form_tpl'] = 'impositions/region_form.html'

        context['data_fields'] = []
        if self.object:
            fields = []
            for loader in self.object.data_loaders.all():
                DataLoader = utils.get_data_loader(loader.path)
                data_loader = DataLoader()
                field_choices = data_loader.get_field_choices('text', loader.prefix)
                fields.extend([(data_loader.verbose_name(), field_choices)])
            context['data_fields'] = fields

        return context

class CompositionUpdateView(FormSetMixin, edit.UpdateView):
    model = models.Composition
    formset_model = models.CompositionRegion
    form_class = forms.CompositionForm
    context_object_name = 'composition'
    success_url = '.'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CompositionUpdateView, self).dispatch(request, *args, **kwargs)

template_list = TemplateListView.as_view()
template_create = TemplateCreateView.as_view()
template_edit = TemplateUpdateView.as_view()
comp_edit = CompositionUpdateView.as_view()
