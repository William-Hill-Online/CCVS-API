import json
import logging
import tempfile

import pyaml
from container_scanning import exceptions
from paclair.handler import PaClair
from rest_framework import status

logger = logging.getLogger(__name__)


def add_image(config, tag):
    try:
        fp = tempfile.NamedTemporaryFile()
        data = pyaml.dump(config)
        fp.write(bytes(data, 'utf-8'))
        fp.seek(0)
        paclair_object = PaClair(fp.name)
        paclair_object.push('Docker', tag)
        obj = paclair_object.analyse('Docker', tag)
    except Exception as err:
        logger.error(err)
        raise exceptions.VendorException(err, status.HTTP_400_BAD_REQUEST)
    else:
        obj = json.loads(obj)
        return obj['ancestry']['name']
    finally:
        fp.close()


def get_vuln(config, image_id):
    try:
        fp = tempfile.NamedTemporaryFile()
        data = pyaml.dump(config)
        fp.write(bytes(data, 'utf-8'))
        fp.seek(0)
        paclair_object = PaClair(fp.name)
        obj = paclair_object._plugins['Docker'].clair.get_ancestry(image_id)
    except Exception as err:
        logger.error(err)
        raise exceptions.VendorException(err, status.HTTP_400_BAD_REQUEST)
    else:
        return obj
    finally:
        fp.close()


def parse_results(whitelist, results):

    new_results = {}

    ancestry = results.get('ancestry')
    for layer in ancestry.get('layers', []):
        detected_features = layer.get('detected_features', [])
        for detected_feature in detected_features:
            for vulnerability in detected_feature.get('vulnerabilities', []):
                # if the vulnerability is in the whitelist
                # should be ignored
                if vulnerability.get('name') in whitelist:
                    continue

                severity = vulnerability.get('severity')
                if severity in ['Critical', 'Defcon1']:
                    key = 'critical_vulns'
                else:
                    # Unknown, Negligible, Low, Medium, High
                    key = severity.lower() + '_vulns'

                if not new_results.get(key):
                    new_results[key] = []

                name = detected_feature.get('name')
                version = detected_feature.get('version')
                new_results[key].append({
                    'package': f'{name}-{version}',
                    'name': vulnerability.get('name'),
                    'fix': vulnerability.get('fixed_by'),
                    'url': vulnerability.get('link'),
                    'severity': vulnerability.get('severity')
                })

    return new_results
