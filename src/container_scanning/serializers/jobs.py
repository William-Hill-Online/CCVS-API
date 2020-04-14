from container_scanning.models import Job
from rest_framework import serializers


class JobSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Job
        fields = (
            'id',
            'status',
            'created_at',
            'updated_at',
            'data',
            'result',
        )
        read_only_fields = (
            'status',
            'created_at',
            'updated_at',
            'result',
        )
