import logging

import requests
from container_scanning import exceptions
from rest_framework import status

logger = logging.getLogger(__name__)


def add_image(config, tag):
    # skip adding image in Trivy
    return tag


def get_vuln(config, image_id):
    if 'url' not in config:
        raise exceptions.VendorException(
            'Missing vendor url', status.HTTP_400_BAD_REQUEST)

    url = config['url'] + '/analysis'
    post_data = {
        'image': image_id
    }

    try:
        response = requests.post(url, data=post_data)
    except requests.exceptions.HTTPError as err:
        raise exceptions.VendorException(
            err, status.HTTP_500_INTERNAL_SERVER_ERROR)
    return response.json()


def parse_results(whitelist, results):
    new_results = {}
    for result in results.get('result', []):
        vulnerabilities = result.get('Vulnerabilities')
        if vulnerabilities:
            for vulnerability in vulnerabilities:
                # if the vulnerability is in the whitelist
                # should be ignored
                if vulnerability.get('VulnerabilityID') in whitelist:
                    continue

                severity = vulnerability.get('Severity')
                # Unknown, Negligible, Low, Medium, High, Critical
                key = severity.lower() + '_vulns'
                if not new_results.get(key):
                    new_results[key] = []

                new_results[key].append({
                    'package_name': vulnerability.get('PkgName'),
                    'package_version': vulnerability.get('InstalledVersion'),
                    'name': vulnerability.get('VulnerabilityID'),
                    'fix': vulnerability.get('FixedVersion'),
                    'url':  vulnerability.get('References'),
                    'severity': vulnerability.get('Severity')
                })

    return new_results
