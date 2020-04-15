from container_scanning.models import Analysis
from rest_framework import serializers


class AnalysisSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Analysis
        fields = (
            'id',
            'status',
            'created_at',
            'updated_at',
            'image',
            'result',
            'vendors',
            'vulnerabilities',
        )
        read_only_fields = (
            'id',
            'status',
            'created_at',
            'updated_at',
            'result',
            'vendors',
            'vulnerabilities',
        )
