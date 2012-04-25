from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('impositions.views',
    url('^templates/$', 'template_list', name='impositions-template-list'),
    url('^templates/create/$', 'template_create', name='impositions-template-create'),
    url('^templates/(?P<pk>\d+)/$', 'template_edit', name='impositions-template-edit'),
    url('^templates/(?P<pk>\d+)/delete/$', 'template_delete', name='impositions-template-delete'),
    url('^comps/(?P<pk>\d+)/$', 'comp_edit', name='impositions-comp-edit'),
)
