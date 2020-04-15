import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models


class Vendor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    credentials = JSONField()

    def __str__(self):
        return self.name


class Analysis(models.Model):

    # list of statuses that analysis can have
    STATUSES = (
        ('pending', 'pending'),
        ('started', 'started'),
        ('finished', 'finished'),
        ('failed', 'failed'),
    )
    RESULTS = (
        ('pending', 'pending'),
        ('passed', 'passed'),
        ('failed', 'failed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(choices=STATUSES, max_length=20, default=STATUSES[0][0])
    result = models.CharField(choices=RESULTS, max_length=20, default=STATUSES[0][0])
    image = models.CharField(max_length=255, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    vulnerabilities = JSONField(null=True)
    vendors = JSONField(null=True)

    def save(self, *args, **kwargs):
        super(Analysis, self).save(*args, **kwargs)
        if self.status == 'pending':
            from .tasks import scan_image

            scan_image.delay(analysis_id=self.id, image=self.image)
