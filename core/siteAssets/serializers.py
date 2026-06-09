#rest files
from rest_framework import serializers

#your files
from .models import HomeImage


class HomeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeImage
        fields = '__all__'






