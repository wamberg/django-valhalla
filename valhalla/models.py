from datetime import datetime

from django.contrib.auth import models as auth_models
from django.db import models

import dispatch


class Deed(models.Model):
    """
    Who said what when as reported by someone.

    ``text`` - what is to be recorded
    ``speaker`` - who said the ``text``
    ``user`` - the authenticated user responsible for creating the db record
    ``deed_date`` - when the Deed was took place
    ``create_date`` - when the Deed was created in the database
    """
    text = models.TextField()
    speaker = models.CharField(max_length=100, db_index=True)
    user = models.ForeignKey(auth_models.User)
    deed_date = models.DateTimeField(default=datetime.utcnow, db_index=True)
    create_date = models.DateTimeField(default=datetime.utcnow)

    class Meta:
        ordering = ['deed_date']

    def dispatch(self, dispatch_list):
        if dispatch_list: 
            for d in dispatch_list:
                dispatch.dispatch_to(d, self.text)

