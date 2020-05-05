import json
import logging

from celery.decorators import task
from container_scanning.models import Vendor
from container_scanning.vendors.initialize import initialize
from rest_framework.exceptions import APIException

from .models import Analysis

LOGGER = logging.getLogger(__name__)


def scan_image_vendor(analysis, vendor):
    """Function that will call function of the vendor and start the scan, get
    results and parser the result."""

    vendor_facade = initialize(vendor.name)

    # Create scan
    image_id = vendor_facade.add_image(
        config=vendor.credentials,
        tag=analysis.image
    )

    # Get scan
    vendor_output = vendor_facade.get_vuln(
        config=vendor.credentials,
        image_id=image_id
    )

    # Parse results and filter whitelist
    result = vendor_facade.parse_results(
        whitelist=analysis.whitelist.get(vendor.name, []),
        results=vendor_output
    )

    output = {
        'output': json.dumps(vendor_output),
        'image_id': image_id
    }

    return result, output


@task(name='container_scanning.tasks.scan_image')
def scan_image(analysis_id):
    """Function that will scan image, update status and results of an
    analysis."""

    analysis = Analysis.objects.get(id=analysis_id)
    analysis.status = 'started'
    analysis.save()

    try:
        vendors = Vendor.objects.all()
        if vendors:
            for vendor in vendors:
                result, output = scan_image_vendor(analysis, vendor)
                analysis.ccvs_results[vendor.name] = result
                analysis.vendors[vendor.name] = output
                analysis.save()
        else:
            analysis.errors.append('Vendors not registred')

    except (
        APIException,
        Exception
    ) as err:
        LOGGER.exception(msg={'error': str(err)})
        analysis.errors.append(str(err))
        analysis.save()

    finally:
        vulns = [item for item in analysis.ccvs_results.values() if item]
        analysis.result = 'failed' if vulns or analysis.errors else 'passed'
        analysis.status = 'finished'
        analysis.save()
