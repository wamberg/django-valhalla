"""
Converts valhalla models into formats serialized for the API.
"""
from datetime import datetime

from django import forms
from django.contrib.auth import models as auth_models
from django.core import serializers

from django_restapi import authentication as rest_authentication
from django_restapi import model_resource as rest_model_resource
from django_restapi import receiver as rest_receiver
from django_restapi import responder as rest_responder

from valhalla import models as valhalla_models

from django.utils import simplejson


class BasicAuthenticatedJSONReceiver(rest_receiver.JSONReceiver):
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
            raise rest_receiver.InvalidFormData
        if len(deserialized_objects) != 1:
            raise rest_receiver.InvalidFormData
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


class DeedCollection(rest_model_resource.Collection):
    """
    Handles custom queries for Deed objects.
    """
    def __init__(self):
        super(DeedCollection, self).__init__(
            queryset=valhalla_models.Deed.objects.all(),
            permitted_methods = ('GET', 'POST'),
            receiver = BasicAuthenticatedJSONReceiver(),
            responder = rest_responder.JSONResponder(paginate_by=10),
            authentication = rest_authentication.HttpBasicAuthentication())

    def read(self, request):
        """
        The request may contain queries that relate to the queryset.
        The following queries affect the queryset:

        start:
            earliest date the queryset should contain
        """
        start_query = request.GET.get('start')
        if start_query:
            try:
                start_date = datetime.strptime(start_query, '%Y-%m-%d')
            except ValueError:
                # start query came in an unexpected format
                return self.responder.error(request, 400)
            self.queryset = self.queryset.filter(deed_date__gte=start_date)

        return self.responder.list(request, self.queryset)

    def _extract_dispatch(self, request):
        return simplejson.loads(request.raw_post_data)[0].get('dispatch', None)

    def create(self, request):
        """ 
            Creates a resource with attributes given by POST, then
            redirects to the resource URI. 
        """
        # Create form filled with POST data
        ResourceForm = forms.models.modelform_factory(self.queryset.model, form=self.form_class)
        data = self.receiver.get_post_data(request)
        form = ResourceForm(data)

        # If the data contains no errors, save the model,
        # return a "201 Created" response with the model's
        # URI in the location header and a representation
        # of the model in the response body.
        if form.is_valid():
            dispatch = self._extract_dispatch(request)
            new_model = form.save()
            new_model.dispatch(dispatch)
            model_entry = self.entry_class(self, new_model)
            response = model_entry.read(request)
            response.status_code = 201 
            response['Location'] = model_entry.get_url()
            return response

        # Otherwise return a 400 Bad Request error.
        raise InvalidModelData(form.errors)

json_deed_resource_list = DeedCollection()
