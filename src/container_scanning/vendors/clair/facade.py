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
        raise exceptions.VendorException(
            err, status.HTTP_400_BAD_REQUEST)
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
        raise exceptions.VendorException(
            err, status.HTTP_400_BAD_REQUEST)
    else:
        return obj
    finally:
        fp.close()
