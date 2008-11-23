"""
Converts valhalla models into formats serialized for the API.
"""

from django import forms
from django.contrib.auth import models as auth_models
from django.core import serializers

from django_restapi import authentication
from django_restapi import model_resource
from django_restapi import receiver
from django_restapi import responder

from valhalla import models as valhalla_models


class BasicAuthenticatedJSONReceiver(receiver.JSONReceiver):
    """
    This receiver not only grabs the raw_post_data from the request but also
    grabs the User from the request.
    """
    def get_data(self, request, method):
        """
        We assume the model object has a ``user`` attribute that we set to
        the basic authenticated user.
        """
        try:
            deserialized_objects = list(
                    serializers.deserialize(
                        self.format, request.raw_post_data))
        except serializers.base.DeserializationError:
            raise receiver.InvalidFormData
        if len(deserialized_objects) != 1:
            raise receiver.InvalidFormData
        model = deserialized_objects[0].object
            
        # add authenticated user to deserialized data
        (authmeth, auth) = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
        if authmeth.lower() != 'basic':
            return False
        auth = auth.strip().decode('base64')
        username, password = auth.split(':', 1)
        user = auth_models.User.objects.get(username=username)
        model.user = user

        return forms.model_to_dict(model)


json_deed_resource_list = model_resource.Collection(
        queryset = valhalla_models.Deed.objects.all(),
        permitted_methods = ('GET', 'POST'),
        receiver = BasicAuthenticatedJSONReceiver(),
        responder = responder.JSONResponder(paginate_by=10),
        authentication = authentication.HttpBasicAuthentication())
