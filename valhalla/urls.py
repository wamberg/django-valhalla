from django.conf.urls.defaults import *

urlpatterns = patterns('',
        url(r'^$',
            'valhalla.views.deed_list',
            name='valhalla_deed_list'),
        url(r'^deed/$',
            'valhalla.views.deed_detail',
            name='valhall_deed_detail'),
)
