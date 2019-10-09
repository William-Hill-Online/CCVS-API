from container_scannning import exceptions
from container_scannning.models import Image
from container_scannning.models import ImageVendor
from container_scannning.models import Vendor
from container_scannning.serializers import images as szrl_images
from container_scannning.vendors import initialize
from core.permissions import JWTAPIPermission
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView


name_param = openapi.Parameter(
    'name', in_=openapi.IN_QUERY, description='Name of the image',
    type=openapi.TYPE_STRING
)


class ImagesView(APIView):

    permission_classes = [JWTAPIPermission]
    required_scopes = {
        'GET': ['container-scanning/images.read'],
        'POST': ['container-scanning/images.create'],
    }

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: szrl_images.ImageSerializer(many=True)
        },
        manual_parameters=[name_param]
    )
    def get(self, request):
        if request.query_params.get('name'):
            name = request.query_params.get('name')
            images = Image.objects.filter(name=name)
        else:
            images = Image.objects.all()
        serializer = szrl_images.ImageSerializer(images, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            status.HTTP_201_CREATED: szrl_images.ImageSerializer
        },
        request_body=szrl_images.ImageSerializer
    )
    def post(self, request):
        image = request.data

        # Create an image from the above data
        serializer = szrl_images.ImageSerializer(data=image)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


class ImageView(APIView):

    permission_classes = [JWTAPIPermission]
    required_scopes = {
        'GET': ['container-scanning/images.read'],
    }

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: szrl_images.ImageSerializer
        },
    )
    def get(self, request, image_id):
        image = get_object_or_404(Image, pk=image_id)
        serializer = szrl_images.ImageSerializer(image)
        return Response(serializer.data, status.HTTP_200_OK)


class ImageVendorView(APIView):

    permission_classes = [JWTAPIPermission]
    required_scopes = {
        'GET': ['container-scanning/images.read'],
        'POST': ['container-scanning/images.create'],
    }

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: szrl_images.ImageVendorSerializer
        },
    )
    def get(self, request, image_id, vendor_id):
        image_vendor_obj = get_object_or_404(
            ImageVendor, image_id=image_id, vendor_id=vendor_id)
        serializer = szrl_images.ImageVendorSerializer(image_vendor_obj)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            status.HTTP_201_CREATED: szrl_images.ImageVendorSerializer
        },
    )
    def post(self, request, image_id, vendor_id):
        image = get_object_or_404(Image, pk=image_id)
        vendor = get_object_or_404(Vendor, pk=vendor_id)
        data = {
            'image': image_id,
            'vendor': vendor_id
        }
        serializer = szrl_images.ImageVendorSerializer(data=data, partial=True)

        if serializer.is_valid(raise_exception=True):

            try:
                vendor_facade = initialize.initialize(vendor.name)
                img_id = vendor_facade.add_image(
                    vendor.credentials,
                    tag=image.name
                )
            except Exception:
                raise exceptions.VendorException(
                    'Error accessing external API',
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            else:
                data['image_vendor_id'] = img_id
                serializer = szrl_images.ImageVendorSerializer(data=data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()

        return Response(serializer.data, status.HTTP_201_CREATED)


class ImageVendorVulnView(APIView):

    permission_classes = [JWTAPIPermission]
    required_scopes = {
        'GET': ['container-scanning/images.read'],
    }

    def get(self, request, image_id, vendor_id):

        image_vendor_obj = get_object_or_404(
            ImageVendor, image_id=image_id, vendor_id=vendor_id)
        try:
            vendor_facade = initialize.initialize(image_vendor_obj.vendor.name)
            image_vendor = vendor_facade.get_vuln(
                image_vendor_obj=image_vendor_obj)
        except Exception:
            raise exceptions.VendorException(
                'Error accessing external API',
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        else:
            return Response(image_vendor, status.HTTP_200_OK)
