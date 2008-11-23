from django.conf.urls.defaults import *

from valhalla import views


urlpatterns = patterns('',
        url(r'^api/json/deeds/$',
            views.json_deed_resource_list,
            name='valhalla_json_deed_list_api'),
        url(r'^api/json/deeds/(?P<object_id>\d+)/$',
            views.json_deed_resource_list,
            name='valhalla_json_deed_detail_api'),
)
