from datetime import datetime

from django.contrib.auth import models as auth_models
from django.db import models


class Deed(models.Model):
    """
    Who said what when as reported by someone.

    ``text`` - what is to be recorded
    ``speaker`` - who said the ``text``
    ``witness`` - who recorded what the ``speaker`` said
    ``report_date`` - when the Deed was recorded
    ``reporter`` - the authenticated user responsible for creating the db record
    """
    text = models.TextField()
    speaker = models.CharField(max_length=200)
    witness = models.CharField(max_length=200)
    report_date = models.DateTimeField(default=datetime.now)
    reporter = models.ForeignKey(auth_models.User)
