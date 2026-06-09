# django files

# rest files
from rest_framework import status, viewsets, generics
from rest_framework.decorators import action as Action
from rest_framework.response import Response
# your files
from .models import Location, CommunicationWithUs
from .serializers import (
    LocationSerializer,
    CommunicationWithUsSerializer
)


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class CommunicationWithUsViewSet(viewsets.ModelViewSet):
    queryset = CommunicationWithUs.objects.all()
    serializer_class = CommunicationWithUsSerializer
