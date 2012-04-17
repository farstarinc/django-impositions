from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('impositions.views',
    url('^templates/$', 'template_list', name='impositions-template-list'),
    url('^templates/create/$', 'template_create', name='impositions-template-create'),
    url('^templates/(?P<pk>\d+)/$', 'template_edit', name='impositions-template-edit'),
    #url('^comps/create/$', 'comp_editor', name='impositions-comp-create'),
    #url('^comps/(?P<id>\d+)/$', 'comp_editor', name='impositions-comp-edit'),
)
