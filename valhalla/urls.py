from django.conf.urls.defaults import *

from valhalla import api


urlpatterns = patterns('',
        # JSON API
        url(r'^api/json/deeds/$',
            api.json_deed_resource_list,
            name='valhalla_json_deed_list_api'),
        url(r'^api/json/deeds/(?P<object_id>\d+)/$',
            api.json_deed_resource_list,
            name='valhalla_json_deed_detail_api'),
)
