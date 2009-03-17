
from sys import modules
from django.conf import settings
from django.core import exceptions
from python_twitter import Api

class TwitterDispatcher(object):
    def send(self, message):
        try:
            username = settings.VALHALLA_TWITTER_USERNAME
        except AttributeError:
            raise exceptions.ImproperlyConfigured(
                    'You must set a VALHALLA_TWITTER_USERNAME in settings.py.')
        try:
            password = settings.VALHALLA_TWITTER_PASSWORD
        except AttributeError:
            raise exceptions.ImproperlyConfigured(
                    'You must set a VALHALLA_TWITTER_PASSWORD in settings.py.')
        api = Api(username=username, password=password)
        api.PostUpdate(message)
