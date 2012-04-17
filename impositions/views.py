from django import http
from django.views.generic import list, edit
from impositions import models, forms

class TemplateListView(list.ListView):
    model = models.Template
    context_object_name = 'templates'

class TemplateCreateView(edit.CreateView):
    model = models.Template
    context_object_name = 'template'

class TemplateUpdateView(edit.UpdateView):
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
            return http.HttpResponseRedirect('.')
        return super(TemplateUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(TemplateUpdateView, self).get_context_data(**kwargs)
        context['formset_form_tpl'] = 'impositions/region_form.html'

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
