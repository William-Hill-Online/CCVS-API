import importlib


def initialize(name):
    try:
        module = importlib.import_module(f'container_scanning.vendors.{name}.facade')
        return module
    except Exception:
        return False
