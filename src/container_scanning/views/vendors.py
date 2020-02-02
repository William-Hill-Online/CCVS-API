from container_scanning.models import Vendor
from container_scanning.serializers import vendors as srlz_vendors
from core.permissions import JWTAPIPermission
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

name_param = openapi.Parameter(
    'name',
    in_=openapi.IN_QUERY,
    description='Name of the vendor',
    type=openapi.TYPE_STRING,
)


class VendorView(APIView):

    permission_classes = [JWTAPIPermission]
    required_scopes = {
        'GET': ['container-scanning/vendors.read'],
        'PUT': ['container-scanning/vendors.update'],
        'DELETE': ['container-scanning/vendors.delete'],
    }

    @swagger_auto_schema(responses={status.HTTP_200_OK: srlz_vendors.VendorSerializer})
    def get(self, request, vendor_id):
        vendor = get_object_or_404(Vendor, pk=vendor_id)
        serializer = srlz_vendors.VendorSerializer(vendor)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: srlz_vendors.VendorSerializer},
        request_body=srlz_vendors.VendorSerializer,
    )
    def put(self, request, vendor_id):
        saved_vendor = get_object_or_404(Vendor, pk=vendor_id)
        data = request.data
        serializer = srlz_vendors.VendorSerializer(
            instance=saved_vendor, data=data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

    def delete(self, request, vendor_id):
        vendor = get_object_or_404(Vendor, pk=vendor_id)
        vendor.delete()
        return Response(None, status.HTTP_204_NO_CONTENT)


class VendorsView(APIView):
    # permission_classes = [JWTAPIPermission]
    permission_classes = []
    required_scopes = {
        'GET': ['container-scanning/vendors.read'],
        'POST': ['container-scanning/vendors.create'],
    }

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: srlz_vendors.VendorSerializer(many=True)},
        manual_parameters=[name_param],
    )
    def get(self, request):
        if request.query_params.get('name'):
            name = request.query_params.get('name')
            vendors = Vendor.objects.filter(name=name)
        else:
            vendors = Vendor.objects.all()
        serializer = srlz_vendors.VendorSerializer(vendors, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={status.HTTP_201_CREATED: srlz_vendors.VendorSerializer},
        request_body=srlz_vendors.VendorSerializer,
    )
    def post(self, request):
        vendor = request.data

        # Create an vendor from the above data
        serializer = srlz_vendors.VendorSerializer(data=vendor)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)
