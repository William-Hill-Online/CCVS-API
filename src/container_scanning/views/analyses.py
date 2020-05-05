import logging

from container_scanning.models import Analysis
from container_scanning.serializers import analysis as szrl_analysis
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

name_param = openapi.Parameter(
    'name',
    in_=openapi.IN_QUERY,
    description='Name of the image',
    type=openapi.TYPE_STRING,
)

logger = logging.getLogger(__name__)


class AnalysisIdView(APIView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: szrl_analysis.AnalysisSerializer
        }
    )
    def get(self, request, analysis_id):
        analysis_obj = get_object_or_404(Analysis, id=analysis_id)
        serializer = szrl_analysis.AnalysisSerializer(analysis_obj)
        return Response(serializer.data, status.HTTP_200_OK)


class AnalysisView(APIView):
    @swagger_auto_schema(
        responses={status.HTTP_202_ACCEPTED: szrl_analysis.AnalysisSerializer},
        request_body=szrl_analysis.AnalysisSerializer,
    )
    def post(self, request):
        payload = request.data
        data = {
            'image': payload.get('image'),
            'whitelist': payload.get('whitelist', {})
        }

        # Create an image from the above data
        serializer = szrl_analysis.AnalysisSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(serializer.data, status.HTTP_202_ACCEPTED)
