
from sys import modules
from python_twitter import Api

class TwitterDispatcher(object):
    def send(self, message):
        api = Api(username='crewtons', password='XXXXX')
        api.PostUpdate(message)

