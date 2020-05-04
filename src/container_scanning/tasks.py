import logging

from celery.decorators import task
from container_scanning.models import Vendor
from container_scanning.vendors.initialize import initialize
from rest_framework.exceptions import APIException

from .models import Analysis

LOGGER = logging.getLogger(__name__)


def scan_image_vendor(analysis, vendor):
    """Function that will call function of the vendor and start the scan, get
    results and parser the result in a resume."""

    result = {
        'error': None
    }
    try:
        vendor_facade = initialize(vendor.name)
        if vendor_facade:
            image_id = vendor_facade.add_image(
                config=vendor.credentials,
                tag=analysis.image
            )
            results = vendor_facade.get_vuln(
                config=vendor.credentials,
                image_id=image_id
            )
            resume = vendor_facade.get_resume(
                whitelist=analysis.whitelist.get(vendor.name, []),
                results=results
            )
            analysis.vendors[vendor.name] = results
            analysis.vulnerabilities[vendor.name] = resume
            analysis.save()
        else:
            raise Exception('Vendor not initialized')

    except APIException as err:
        result['error'] = err.detail

    except Exception as err:
        result['error'] = str(err)

    finally:
        return result


def scan_image_vendors(analysis):

    vendors = Vendor.objects.all()
    for vendor in vendors:
        yield scan_image_vendor(analysis, vendor)


@task(name='container_scanning.tasks.scan_image')
def scan_image(analysis_id):
    """Function that will scan image, update status and result of anilysis."""

    analysis = Analysis.objects.get(id=analysis_id)
    analysis.status = 'started'
    analysis.save()

    error_control = False
    try:
        for result_vendor in scan_image_vendors(analysis):
            # Check the first error
            if result_vendor.get('error') is not None \
                    and error_control is False:
                error_control = True
                LOGGER.exception(
                    msg={'error': result_vendor.get('error')})

    except Exception as err:
        analysis.status = 'failed'
        analysis.result = 'failed'
        LOGGER.exception(msg={'error': str(err)})

    else:
        if error_control is False:
            vulns = analysis.vulnerabilities.values()
            analysis.status = 'finished'
            analysis.result = 'failed' if \
                [i for i in vulns if i] else 'passed'
        else:
            analysis.status = 'failed'
            analysis.result = 'failed'

    finally:
        analysis.save()
