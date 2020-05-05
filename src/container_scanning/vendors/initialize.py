import importlib
import logging

logger = logging.getLogger(__name__)


def initialize(name):
    try:
        module = importlib.import_module(
            f'container_scanning.vendors.{name}.facade')
    except Exception as error:
        msg_error = f'Error initializing vendor {name}',
        logger.exception(msg={'error': msg_error, 'exception': error})
        raise Exception(msg_error)
    else:
        if not module:
            msg_error = f'Vendor {name} not initialized'
            logger.exception(msg={'error': msg_error})
            raise Exception(msg_error)
        return module
