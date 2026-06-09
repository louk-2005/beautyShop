# django files
from django.urls import path, include

# rest files
from rest_framework.routers import DefaultRouter

# your files
from . import views

app_name = 'contactUs'

router = DefaultRouter()
router.register(r'location', views.LocationViewSet, basename='location')
router.register(r'communication/with/us', views.CommunicationWithUsViewSet, basename='communication-with-us')


urlpatterns = [
    path('', include(router.urls)),
]