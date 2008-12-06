from django.conf.urls.defaults import *

from valhalla import api, forms


urlpatterns = patterns('',
        # JSON API
        url(r'^api/json/deeds/$',
            api.json_deed_resource_list,
            name='valhalla_json_deed_list_api'),
        url(r'^api/json/deeds/(?P<object_id>\d+)/$',
            api.json_deed_resource_list,
            name='valhalla_json_deed_detail_api'),

        # HTML views
        url(r'^deeds/$',
            'django.views.generic.simple.direct_to_template',
            {'template': 'valhalla/deed_list.html',
                'extra_context': {'form': forms.DeedForm()}},
            name='valhalla_deed_list'),
)
