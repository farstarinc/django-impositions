from django import http
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.decorators import method_decorator
from django.views.generic import list as list_views, edit
from impositions import models, forms, utils, helpers

class TemplateBase(object):
    context_object_name = 'template'

    @method_decorator(permission_required('impositions.change_template'))
    def dispatch(self, request, *args, **kwargs):
        return super(TemplateBase, self).dispatch(request, *args, **kwargs)


class TemplateListView(TemplateBase, list_views.ListView):
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

    def dispatch(self, request, *args, **kwargs):
        copy_id = kwargs.pop('copy_id', None)
        response = super(TemplateUpdateView, self).dispatch(request, *args, **kwargs)
        if copy_id:
            copy_from_tpl = models.Template.objects.get(pk=copy_id)
            for region in copy_from_tpl.regions.all():
                # To copy the model field-for-field, we just unset the pk
                region.pk = None
                region.template_id = self.object.id
                region.save()
            template_url = reverse('impositions-template-edit', kwargs={'pk':self.object.pk})
            return http.HttpResponseRedirect(template_url)
        else:
            return response


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
        
        other_templates = models.Template.objects.order_by('-id')
        context['other_templates'] = other_templates.exclude(pk=self.object.pk)

        return context

class TemplateDeleteView(TemplateBase, edit.DeleteView):
    model = models.Template
    def get_success_url(self):
        return reverse('impositions-template-list')

class CompositionUpdateView(helpers.InlineFormSetMixin, edit.UpdateView):
    model = models.Composition
    form_class = forms.CompositionForm
    formset_class = forms.CompositionRegionFormSet
    context_object_name = 'composition'
    success_url = '.'

    def get_success_url(self):
        if self.request.GET.get('next'):
            return self.request.GET['next']
        return super(CompositionUpdateView, self).get_success_url()
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CompositionUpdateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        regions = kwargs.get('regions', None)
        kwargs['formset_form_tpl'] = 'impositions/composition_region_form.html'
        kwargs['composition_thumb'] = self.object.get_thumbnail(regions=regions)
        return super(CompositionUpdateView, self).get_context_data(**kwargs)

class DummyRelatedManager(object):
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

class CompositionPreview(CompositionUpdateView):
    """
    By posting the form to this view, we can get a preview of the
    composition without having to save it.
    """
    template_name = 'impositions/includes/comp_preview.html'

    def form_valid(self, form, formset):
        self.object = form.save(commit=False)
        formset.instance = self.object
        regions = list(self.object.regions.all())
        changed_regions = formset.save(commit=False)
        for region in changed_regions:
            for i,r in enumerate(regions):
                if r.pk == region.pk:
                    regions[i] = region
        context = self.get_context_data(form=form, formset=formset, regions=regions)
        return self.render_to_response(context)

    def get_success_url(self):
        return '.'

template_list = TemplateListView.as_view()
template_create = TemplateCreateView.as_view()
template_edit = TemplateUpdateView.as_view()
template_delete = TemplateDeleteView.as_view()
template_copy = TemplateUpdateView.as_view()
comp_edit = CompositionUpdateView.as_view()
comp_preview = CompositionPreview.as_view()
