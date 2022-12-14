from rest_framework import serializers
from pool.models import Metadata


class GeoServerSerialization(serializers.ModelSerializer):
    """CLASS to serialize 'serializers.metadata_copy' model data
    """

    def create(self, data):
        """METHOD for saving metadata_copy serialized data on database

        Args:
            data (dict): BNDESTransaction serialized data
        Returns:
            dict: BNDESTransaction serialized data
        """

        response_ope, obj = Metadata.objects.filter(**data).get_or_create(**data)
        if obj is False:
            response_ope.save()

        return response_ope

    class Meta:
        model = Metadata
        fields = '__all__'
