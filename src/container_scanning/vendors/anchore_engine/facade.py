from anchorecli.clients import apiexternal
from container_scanning import exceptions
from rest_framework import status


def get_image(image_vendor_obj):
    config = image_vendor_obj.vendor.credentials
    image_id = image_vendor_obj.vendor_image_internal_id
    image_vendor = apiexternal.get_image(config, image_id=image_id)

    if image_vendor['success'] is False:
        raise exceptions.VendorException(
            image_vendor['error'], status.HTTP_500_INTERNAL_SERVER_ERROR)
    return image_vendor['payload']


def add_image(config, tag):
    image_vendor = apiexternal.add_image(config, tag=tag)
    if image_vendor['success'] is False:
        raise exceptions.VendorException(
            image_vendor['error'], status.HTTP_400_BAD_REQUEST)
    else:
        img_id = image_vendor['payload'][0]['imageDigest']

        return img_id


def get_vuln(image_vendor_obj):
    config = image_vendor_obj.vendor.credentials
    image_digest = image_vendor_obj.vendor_image_internal_id
    query_group = 'vuln'
    query_type = 'all'
    image_vendor = apiexternal.query_image(
        config, imageDigest=image_digest, query_group=query_group,
        query_type=query_type, vendor_only=True)

    if image_vendor['success'] is False:
        raise exceptions.VendorException(
            image_vendor['error'], status.HTTP_500_INTERNAL_SERVER_ERROR)
    return image_vendor['payload']
