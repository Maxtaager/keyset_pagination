from django.db import models
import uuid


class KeySetModel(models.Model):
    # let django create the id field
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    name = models.TextField()

    def __unicode__(self):
        return unicode(self.id)