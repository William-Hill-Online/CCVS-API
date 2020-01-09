import logging

from container_scanning.models import Job
from container_scanning.serializers import jobs as szrl_jobs
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

logger = logging.getLogger(__name__)


class JobView(APIView):

    @swagger_auto_schema(
        responses={
            status.HTTP_202_ACCEPTED: szrl_jobs.JobSerializer
        }
    )
    def get(self, request, job_id):
        job_obj = get_object_or_404(Job, id=job_id)
        serializer = szrl_jobs.JobSerializer(job_obj)
        return Response(serializer.data, status.HTTP_200_OK)


class JobsView(APIView):
    @swagger_auto_schema(
        responses={
            status.HTTP_202_ACCEPTED: szrl_jobs.JobSerializer
        },
        request_body=szrl_jobs.JobSerializer
    )
    def post(self, request):
        payload = request.data
        data = {
            'data': payload.get('data'),
            'type': payload.get('type'),
        }

        # Create an image from the above data
        serializer = szrl_jobs.JobSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(serializer.data, status.HTTP_202_ACCEPTED)
