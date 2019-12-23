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
