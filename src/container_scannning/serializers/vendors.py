from container_scannning.models import Vendor
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class VendorSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(
        max_length=100,
        validators=[UniqueValidator(queryset=Vendor.objects.all())]
    )
    credentials = serializers.JSONField()

    class Meta:
        model = Vendor
        fields = ('id', 'name', 'credentials')
        read_only_fields = ('id',)

    def create(self, validated_data):
        return Vendor.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.credentials = validated_data.get(
            'credentials', instance.credentials)

        instance.save()
        return instance
