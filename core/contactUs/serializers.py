# rest files
from rest_framework import serializers

# your files
from .models import Location, CommunicationWithUs



class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class CommunicationWithUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationWithUs
        fields = '__all__'