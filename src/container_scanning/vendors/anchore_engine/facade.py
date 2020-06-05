import logging

from anchorecli.clients import apiexternal
from container_scanning import exceptions
from core.decorators import retry
from rest_framework import status

logger = logging.getLogger(__name__)


msg_wait = [
    'image is not analyzed - analysis_status: not_analyzed',
    'image is not analyzed - analysis_status: analyzing',
]


def add_image(config, tag):
    image_vendor = apiexternal.add_image(
        config, tag=tag, force=True, autosubscribe=False)
    if image_vendor['success'] is False:
        raise exceptions.VendorException(
            image_vendor['error'], status.HTTP_400_BAD_REQUEST)
    else:
        img_id = image_vendor['payload'][0]['imageDigest']

        return img_id


@retry(exceptions=exceptions.AnchoreNotAnalyzed,
       tries=20,
       delay=20,
       backoff=3,
       logger=logger)
def get_vuln(config, image_id):
    query_group = 'vuln'
    query_type = 'all'
    image_vendor = apiexternal.query_image(
        config, imageDigest=image_id, query_group=query_group,
        query_type=query_type, vendor_only=True)

    if image_vendor['success'] is False:
        if image_vendor['error'].get('message') in msg_wait:
            raise exceptions.AnchoreNotAnalyzed(
                image_vendor['error'], status.HTTP_500_INTERNAL_SERVER_ERROR)
        raise exceptions.VendorException(
            image_vendor['error'], status.HTTP_500_INTERNAL_SERVER_ERROR)
    return image_vendor['payload']


def parse_results(whitelist, results):

    new_results = {}

    for vulnerability in results.get('vulnerabilities'):
        # if the vulnerability is in the whitelist
        # should be ignored
        if vulnerability.get('vuln') in whitelist:
            continue

        severity = vulnerability.get('severity')
        # Unknown, Negligible, Low, Medium, High, Critical
        key = severity.lower() + '_vulns'

        if not new_results.get(key):
            new_results[key] = []

        new_results[key].append({
            'package': vulnerability.get('package'),
            'name': vulnerability.get('vuln'),
            'fix': vulnerability.get('fix'),
            'url': vulnerability.get('url'),
            'severity': vulnerability.get('severity')
        })

    return new_results
