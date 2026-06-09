from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HomeImagesViewSets

app_name = 'assets'

router = DefaultRouter()
router.register(r'homeImages', HomeImagesViewSets, basename='homeImages')

urlpatterns = [
    path('', include(router.urls)),
]
