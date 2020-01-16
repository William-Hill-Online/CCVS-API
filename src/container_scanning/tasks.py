from functools import wraps

from celery.decorators import task
from container_scanning.models import Vendor
from container_scanning.vendors.initialize import initialize

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


def scan_image_vendor(image_tag, vendor):
    try:
        vendor_facade = initialize(vendor.name)
        if vendor_facade:
            image_id = vendor_facade.add_image(
                vendor.credentials, tag=image_tag)
            image_vendor = vendor_facade.get_vuln(
                vendor.credentials, image_id=image_id)
        else:
            raise Exception('Vendor not initialized')
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
