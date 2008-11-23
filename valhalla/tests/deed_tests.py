"""
Test the deed API.
"""
from os import path
import binascii

from django.contrib.auth import models as auth_models
from django.core import serializers
from django.core import urlresolvers
from django.test import TestCase

from valhalla import models as valhalla_models

TESTS_DIR = path.dirname(__file__)


class DeedTest(TestCase):
    """
    Test the views related to a Deed object.
    """
    fixtures = [path.join(TESTS_DIR, f) for f in ('deeds.json',)]

    def __init__(self, methodName='runTest'):
        """
        Establish easy access to our test user.
        """
        super(DeedTest, self).__init__(methodName)
        self.test_user = None

    def setUp(self):
        """
        Create a test User so that deeds.json User field is valid
        """
        test_user = auth_models.User(username='tdanza')
        test_user.set_password('testpass')
        test_user.save()
        self.test_user = test_user

    def tearDown(self):
        """
        Delete our test User.
        """
        test_user = auth_models.User.objects.get(username='tdanza')
        test_user.delete()
        self.test_user = None

    def test_deed_post(self):
        """
        Ensure that new Deeds can be created through a valid json POST or
        fails well otherwise.
        """
        # establish varilable for Deed creation and checking
        text = 'test deed post'
        speaker = 'jimmy'
        witness = 'johnny'

        # create and POST a new Deed
        # we assign a user_id to the Deed but the actual user is assigned
        # by our custom AuthenticatedJSONRecevier
        headers = {'HTTP_AUTHORIZATION': 'Basic %s' % (
            binascii.b2a_base64('tdanza:testpass')[:-1])}
        new_deed = valhalla_models.Deed(
                text=text,
                speaker=speaker,
                witness=witness,
                user_id=1)
        serialized_deed = serializers.serialize('json', [new_deed])
        serialized_deed = serialized_deed.replace('"pk": null', '"pk": 1')
        response = self.client.post(
                urlresolvers.reverse('valhalla_json_deed_list_api'),
                data=serialized_deed,
                content_type='application/json',
                **headers)

        # assert we created the Deed
        self.assertEquals(response.status_code, 201)
        deed_check = valhalla_models.Deed.objects.get(text=text)
        self.assertEquals(new_deed.text, deed_check.text)
        self.assertEquals(new_deed.speaker, deed_check.speaker)
        self.assertEquals(new_deed.witness, deed_check.witness)
        self.assertEquals(deed_check.user.id, self.test_user.id)
        


    def test_forbidden_access(self):
        """
        Ensure a request that doesn't contain the correct basic authentication
        is forbidden.
        """
        # establish varilable for Deed creation and checking
        text = 'test forbidden access'
        speaker = 'jimmy'
        witness = 'johnny'

        # create and POST a new Deed
        new_deed = valhalla_models.Deed(
                text=text,
                speaker=speaker,
                witness=witness,
                user_id=1)
        serialized_deed = serializers.serialize('json', [new_deed])
        serialized_deed = serialized_deed.replace('"pk": null', '"pk": 1')
        response = self.client.post(
                urlresolvers.reverse('valhalla_json_deed_list_api'),
                data=serialized_deed,
                content_type='application/json')
        self.assertEquals(response.status_code, 401)

        # assert authenticated user's can get to our api
        response = self.client.get(
                urlresolvers.reverse('valhalla_json_deed_list_api'))
        self.assertEquals(response.status_code, 401)

        response = self.client.get(
                urlresolvers.reverse('valhalla_json_deed_list_api'), args=(1,))
        self.assertEquals(response.status_code, 401)
