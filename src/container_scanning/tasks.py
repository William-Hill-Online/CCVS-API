from functools import wraps

from celery.decorators import task
from container_scanning.models import ImageVendor
from container_scanning.models import Vendor
from container_scanning.serializers import images as szrl_images
from container_scanning.vendors import initialize
from rest_framework.generics import get_object_or_404

from .models import Job


def update_job(fn):
    """Decorator that will update Job with result of the function."""

    @wraps(fn)
    def wrapper(job_id, *args, **kwargs):

        job = Job.objects.get(id=job_id)
        job.status = 'started'
        job.save()
        try:
            # execute the function fn
            result = fn(*args, **kwargs)
            job.result = result
            job.status = 'finished'
            job.save()
        except Exception as err:
            job.result = {'err': str(err)}
            job.status = 'failed'
            job.save()
    return wrapper


@task(name='container_scanning.tasks.add_scan')
def add_scan(image_id, vendor_id, force=False):
    try:
        image_vendor_obj = get_object_or_404(
            ImageVendor,
            image_id=image_id,
            vendor_id=vendor_id
        )
        serializer = szrl_images.ImageVendorSerializer(image_vendor_obj)

        vendor_facade = initialize.initialize(image_vendor_obj.vendor.name)
        img_id = vendor_facade.add_image(
            image_vendor_obj.vendor.credentials,
            tag=image_vendor_obj.image.name,
            force=force
        )
    except Exception as err:
        raise Exception(err)
    else:
        data = {'image_vendor_id': img_id}
        serializer = szrl_images.ImageVendorSerializer(
            instance=image_vendor_obj,
            data=data,
            partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()


def scan_image_vendor(image_tag, vendor):
    try:
        vendor_facade = initialize.initialize(vendor.name)
        image_id = vendor_facade.add_image(
            vendor.credentials, tag=image_tag)
        image_vendor = vendor_facade.get_vuln(
            vendor.credentials, image_id=image_id)
    except Exception as err:
        raise Exception(err)
    else:
        return image_vendor


def scan_image_vendors(image_tag):

    vendors = Vendor.objects.all()
    for vendor in vendors:
        try:
            result = scan_image_vendor(image_tag, vendor)
        except Exception as err:
            yield (vendor.name, str(err))
        else:
            yield (vendor.name, result)


@task(name='container_scanning.tasks.scan_image')
@update_job
def scan_image(data):

    image_tag = data.get('image')
    if not image_tag:
        raise Exception('Image was not sending')
    results = {}
    for result in scan_image_vendors(image_tag):
        results[result[0]] = result[1]

    return results


TASK_MAPPING = {
    'scan_image': scan_image,
}
