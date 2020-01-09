import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models


class Vendor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    credentials = JSONField()

    def __str__(self):
        return self.name


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    vendors = models.ManyToManyField(Vendor, through='ImageVendor')

    def __str__(self):
        return self.name


class ImageVendor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    vendor_image_internal_id = models.CharField(max_length=200)

    class Meta:
        unique_together = (('vendor', 'image'))


class Job(models.Model):

    # currently, available types of job are:
    TYPES = (
        ('scan_image', 'scan_image'),
    )

    # list of statuses that job can have
    STATUSES = (
        ('pending', 'pending'),
        ('started', 'started'),
        ('finished', 'finished'),
        ('failed', 'failed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(choices=TYPES, max_length=20)
    status = models.CharField(
        choices=STATUSES, max_length=20, default=STATUSES[0][0])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    data = JSONField()
    result = JSONField(null=True)

    def save(self, *args, **kwargs):
        super(Job, self).save(*args, **kwargs)
        if self.status == 'pending':
            from .tasks import TASK_MAPPING
            task = TASK_MAPPING[self.type]
            task.delay(job_id=self.id, data=self.data)
