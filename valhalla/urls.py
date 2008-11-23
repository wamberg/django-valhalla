from django.conf.urls.defaults import *

from valhalla import views


urlpatterns = patterns('',
        url(r'^$',
            views.json_deed_resource,
            name='valhalla_json_deed_api'),
)
