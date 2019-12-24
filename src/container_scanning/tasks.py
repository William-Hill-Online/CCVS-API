from celery.decorators import task
from container_scanning.models import ImageVendor
from container_scanning.serializers import images as szrl_images
from container_scanning.vendors import initialize
from rest_framework.generics import get_object_or_404


@task(name='container_scanning.tasks.add_scan')
def add_scan(image_id, vendor_id, force=False):
    try:
        image_vendor_obj = get_object_or_404(
            ImageVendor,
            image_id=image_id,
            vendor_id=vendor_id
        )
        serializer = szrl_images.ImageVendorSerializer(image_vendor_obj)

        vendor_facade = initialize.initialize(image_vendor_obj.vendor.name)
        img_id = vendor_facade.add_image(
            image_vendor_obj.vendor.credentials,
            tag=image_vendor_obj.image.name,
            force=force
        )
    except Exception as err:
        raise Exception(err)
    else:
        data = {'image_vendor_id': img_id}
        serializer = szrl_images.ImageVendorSerializer(
            instance=image_vendor_obj,
            data=data,
            partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
