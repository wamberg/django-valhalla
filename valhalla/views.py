from django import http
from django.core import paginator
from django.core import serializers

from django_restapi import model_resource
from django_restapi import receiver
from django_restapi import responder
from valhalla import models as valhalla_models


json_deed_resource = model_resource.Collection(
        queryset = valhalla_models.Deed.objects.all(),
        permitted_methods = ('GET', 'POST'),
        receiver = receiver.JSONReceiver(),
        responder = responder.JSONResponder(paginate_by=10))
