from rest_framework import serializers

from gestion_association.models.animal import Animal


class AnimalSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Animal
        fields = ('id', 'nom')