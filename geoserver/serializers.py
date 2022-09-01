from rest_framework import serializers
from .models import Metadados


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

        response_ope, obj = Metadados.objects.filter(**data).get_or_create(**data)

        if obj == False:
            response_ope.save()

        return response_ope

    class Meta:
        model = Metadados
        fields = '__all__'
