from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.decorators import method_decorator
from django.views.generic import list, edit
from impositions import models, forms, utils, helpers

class TemplateBase(object):
    context_object_name = 'template'

    @method_decorator(permission_required('impositions.change_template'))
    def dispatch(self, request, *args, **kwargs):
        return super(TemplateBase, self).dispatch(request, *args, **kwargs)


class TemplateListView(TemplateBase, list.ListView):
    model = models.Template
    context_object_name = 'templates'

class TemplateCreateView(TemplateBase, edit.CreateView):
    model = models.Template
    form_class = forms.TemplateForm
    
    def get_success_url(self):
        return reverse('impositions-template-edit', kwargs={'pk':self.object.pk})

class TemplateUpdateView(TemplateBase, helpers.InlineFormSetMixin, edit.UpdateView):
    model = models.Template
    form_class = forms.TemplateForm
    formset_class = forms.TemplateRegionFormSet
    success_url = '.'

    def form_valid(self, form, formset):
        response = super(TemplateUpdateView, self).form_valid(form, formset)
        msg = 'Template successfully saved.'
        messages.add_message(self.request, messages.INFO, msg)
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

class TemplateDeleteView(TemplateBase, edit.DeleteView):
    def get_success_url(self):
        return reverse('impositions-template-list')

class CompositionUpdateView(helpers.InlineFormSetMixin, edit.UpdateView):
    model = models.Composition
    form_class = forms.CompositionForm
    formset_class = forms.CompositionRegionFormSet
    context_object_name = 'composition'
    success_url = '.'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CompositionUpdateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['formset_form_tpl'] = 'impositions/composition_region_form.html'
        return super(CompositionUpdateView, self).get_context_data(**kwargs)


template_list = TemplateListView.as_view()
template_create = TemplateCreateView.as_view()
template_edit = TemplateUpdateView.as_view()
template_delete = TemplateDeleteView.as_view(model=models.Template)
comp_edit = CompositionUpdateView.as_view()
