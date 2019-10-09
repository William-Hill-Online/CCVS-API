from container_scannning.models import Image
from container_scannning.models import ImageVendor
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.validators import UniqueValidator


class ImageSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(
        max_length=255,
        validators=[UniqueValidator(queryset=Image.objects.all())]
    )

    class Meta:
        model = Image
        fields = ('id', 'name')
        read_only_fields = ('id',)


class ImageVendorSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    image_vendor_id = serializers.CharField(
        max_length=200,
        source='vendor_image_internal_id',
    )

    class Meta:
        model = ImageVendor
        fields = ('id', 'vendor', 'image', 'image_vendor_id')
        read_only_fields = ('id',)

        validators = [
            UniqueTogetherValidator(
                queryset=ImageVendor.objects.all(),
                fields=('image', 'vendor'),
                message='Image by vendor must be unique.'
            )
        ]
