from django import http
from django.views.generic import list, edit
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from impositions import models, forms, utils

class Base(object):
    @method_decorator(permission_required('impositions.change_template'))
    def dispatch(self, request, *args, **kwargs):
        return super(Base, self).dispatch(request, *args, **kwargs)

class TemplateListView(Base, list.ListView):
    model = models.Template
    context_object_name = 'templates'

class TemplateCreateView(Base, edit.CreateView):
    model = models.Template
    context_object_name = 'template'
    form_class = forms.TemplateForm

class TemplateUpdateView(Base, edit.UpdateView):
    model = models.Template
    context_object_name = 'template'
    form_class = forms.TemplateForm

    def form_valid(self, form):
        context = self.get_context_data()
        region_formset = context['region_formset']
        if region_formset.is_valid():
            self.object = form.save()
            region_formset.instance = self.object
            region_formset.save()
            msg = 'Template successfully saved.'
            messages.add_message(self.request, messages.SUCCESS, msg)
            return http.HttpResponseRedirect('.')
        return super(TemplateUpdateView, self).form_valid(form)

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

        if self.request.POST: 
            region_formset = forms.TemplateRegionFormSet(self.request.POST, 
                self.request.FILES, instance=self.object)
        else:
            region_formset = forms.TemplateRegionFormSet(instance=self.object)

        context.update(region_formset=region_formset)
        return context

template_list = TemplateListView.as_view()
template_create = TemplateCreateView.as_view()
template_edit = TemplateUpdateView.as_view()
