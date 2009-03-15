"""
Test the deed API.
"""
from datetime import datetime
from os import path
import binascii

from django.contrib.auth import models as auth_models
from django.core import serializers
from django.core import urlresolvers
from django.test import TestCase

from valhalla import dispatch
from valhalla import models as valhalla_models

TESTS_DIR = path.dirname(__file__)
TEST_USERNAME = 'tdanza'
TEST_PASSWORD = 'testpass'


def generate_auth_headers():
    """
    Generate the HTTP headers needed for basic HTTP_AUTHORIZATION.
    """
    return {'HTTP_AUTHORIZATION': 'Basic %s' % (
        binascii.b2a_base64('%s:%s' % (TEST_USERNAME, TEST_PASSWORD))[:-1])}


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
        test_user = auth_models.User(username=TEST_USERNAME)
        test_user.set_password(TEST_PASSWORD)
        test_user.save()
        self.test_user = test_user

        # setup dispatch catcher
        dispatch.OUTBOUND = []
        # setup dummy dispatcher
        self.original_dispatchers = dispatch.DISPATCHERS
        for key in dispatch.DISPATCHERS.keys():
            dispatch.DISPATCHERS[key] = dispatch.TestDispatcher

    def tearDown(self):
        """
        Delete our test User.
        """
        test_user = auth_models.User.objects.get(username=TEST_USERNAME)
        test_user.delete()
        self.test_user = None

        del dispatch.OUTBOUND
        dispatch.DISPATCHERS = self.original_dispatchers

    def test_deed_post(self):
        """
        Ensure that new Deeds can be created through a valid json POST or
        fails well otherwise.
        """
        # establish varilable for Deed creation and checking
        text = 'test deed post'
        speaker = 'jimmy'

        # create and POST a new Deed
        # we assign a user_id to the Deed but the actual user is assigned
        # by our custom AuthenticatedJSONRecevier
        new_deed = valhalla_models.Deed(
                text=text,
                speaker=speaker,
                user_id=1)
        serialized_deed = serializers.serialize('json', [new_deed])
        serialized_deed = serialized_deed.replace('"pk": null', '"pk": 1')
        headers = generate_auth_headers()
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
        self.assertEquals(deed_check.user.id, self.test_user.id)
        
    def test_unauthorized_post(self):
        """
        Ensure a request that doesn't contain the correct basic authentication
        is forbidden.
        """
        # establish varilable for Deed creation and checking
        text = 'test forbidden access'
        speaker = 'jimmy'

        # create and POST a new Deed
        new_deed = valhalla_models.Deed(
                text=text,
                speaker=speaker,
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

    def test_get_list(self):
        """
        Test an authorized GET works and an unauthorized GET does not.
        """
        headers = generate_auth_headers()
        # test an authorized GET
        response = self.client.get(
                urlresolvers.reverse('valhalla_json_deed_list_api'), **headers)
        self.assertEquals(response.status_code, 200)
        deeds = list(serializers.deserialize('json', response.content))
        self.assert_(deeds)

        # test an unauthorized GET
        response = self.client.get(
                urlresolvers.reverse('valhalla_json_deed_list_api'))
        self.assertEquals(response.status_code, 401)

    def test_get_detail(self):
        """
        Test an authorized GET works for a single Deed and an
        unauthorized GET does not.
        """
        headers = generate_auth_headers()
        # test an authorized GET
        response = self.client.get(
                urlresolvers.reverse('valhalla_json_deed_detail_api', args=[1]), **headers)
        self.assertEquals(response.status_code, 200)
        deed = list(serializers.deserialize('json', response.content))
        self.assert_(deed)

        # test an unauthorized GET
        response = self.client.get(
                urlresolvers.reverse('valhalla_json_deed_detail_api', args=[1]))
        self.assertEquals(response.status_code, 401)
        
    def test_get_with_start_query(self):
        """
        Test a GET request that includes the ``start`` query.
        """
        headers = generate_auth_headers()
        # test a well-formatted date
        response = self.client.get(
                urlresolvers.reverse('valhalla_json_deed_list_api'),
                {'start': '2008-11-24'}, **headers)
        self.assertEquals(response.status_code, 200)
        deeds = list(serializers.deserialize('json', response.content))
        self.assert_(deeds)
        self.assert_(not [deed for deed in deeds
            if deed.object.deed_date < datetime(2008, 11, 24)])

        # test a poorly-formatted date
        response = self.client.get(
                urlresolvers.reverse('valhalla_json_deed_list_api'),
                {'start': '08-11-24'}, **headers)
        self.assertEquals(response.status_code, 400)

    def test_dispatch_post(self):
        """
        Test our dispatch code
        """
        # establish varilable for Deed creation and checking
        text = 'test deed post'
        speaker = 'jimmy'

        # create and POST a new Deed
        # we assign a user_id to the Deed but the actual user is assigned
        # by our custom AuthenticatedJSONRecevier
        new_deed = valhalla_models.Deed(
                text=text,
                speaker=speaker,
                user_id=1)
        dispatch_json = '"dispatch": ["twitter"]'
        serialized_deed = serializers.serialize('json', [new_deed])
        serialized_deed = serialized_deed.replace('"pk": null', '"pk": 1')
        serialized_deed = serialized_deed.replace(
                '"fields"', '"dispatch": ["twitter"], "fields"')
        headers = generate_auth_headers()
        response = self.client.post(
                urlresolvers.reverse('valhalla_json_deed_list_api'),
                data=serialized_deed,
                content_type='application/json',
                **headers)
        self.assert_(text in dispatch.OUTBOUND)

        # assert we created the Deed
        self.assertEquals(response.status_code, 201)
        deed_check = valhalla_models.Deed.objects.get(text=text)
        self.assertEquals(new_deed.text, deed_check.text)
        self.assertEquals(new_deed.speaker, deed_check.speaker)
        self.assertEquals(deed_check.user.id, self.test_user.id)
