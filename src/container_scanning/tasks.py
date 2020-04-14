from functools import wraps

from celery.decorators import task
from container_scanning.models import Vendor
from container_scanning.vendors.initialize import initialize

from .models import Analysis


def update_analysis(fn):
    """Decorator that will update Analysis with result of the function."""

    @wraps(fn)
    def wrapper(analysis_id, *args, **kwargs):
        analysis = Analysis.objects.get(id=analysis_id)
        analysis.status = 'started'
        analysis.save()
        try:
            # execute the function fn
            vendors, vulnerabilities = fn(*args, **kwargs)
            analysis.status = 'finished'
            analysis.result = 'failed' if \
                [i for i in vulnerabilities.values() if i] else 'passed'
            analysis.vulnerabilities = vulnerabilities
            analysis.vendors = vendors
            analysis.save()
        except Exception as err:
            analysis.vendors = {'err': str(err)}
            analysis.vulnerabilities = {}
            analysis.result = 'failed'
            analysis.status = 'failed'
            analysis.save()

    return wrapper


def scan_image_vendor(image_tag, vendor):
    try:
        vendor_facade = initialize(vendor.name)
        if vendor_facade:
            image_id = vendor_facade.add_image(vendor.credentials, tag=image_tag)
            image_vendor = vendor_facade.get_vuln(vendor.credentials, image_id=image_id)
            resume = vendor_facade.get_resume(image_vendor)
        else:
            raise Exception('Vendor not initialized')
    except Exception as err:
        raise Exception(err)
    else:
        return (image_vendor, resume)


def scan_image_vendors(image_tag):

    vendors = Vendor.objects.all()
    for vendor in vendors:
        try:
            vendor_result = scan_image_vendor(image_tag, vendor)
        except Exception as err:
            yield (vendor.name, str(err), None)
        else:
            yield (vendor.name, vendor_result[0], vendor_result[1])


@task(name='container_scanning.tasks.scan_image')
@update_analysis
def scan_image(image):
    if not image:
        raise Exception('Image was not sending')
    vulnerabilities = {}
    vendors = {}
    for result in scan_image_vendors(image):
        vendors[result[0]] = result[1]
        vulnerabilities[result[0]] = result[2]

    return vendors, vulnerabilities
