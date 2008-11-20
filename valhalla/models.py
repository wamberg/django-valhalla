from django.db import models

class Deed(models.Model):
    """
    Who said what when as reported by someone.
    """
    text = models.TextField()
    speaker = models.CharField(max_length=200)
    reporter = models.CharField(max_length=200)
    report_date = models.DateTimeField()
