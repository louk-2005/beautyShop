# rest files
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny

# your files
from .models import HomeImage
from .serializers import (
    HomeImageSerializer,
)


class HomeImagesViewSets(viewsets.ModelViewSet):
    queryset = HomeImage.objects.all()
    serializer_class = HomeImageSerializer
    permission_classes = (AllowAny,)


