from rest_framework import serializers
from .models import CenterPoints
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.gis.geos import Point

class CenterPointsLocationData(GeoFeatureModelSerializer):
    class Meta:
        model = CenterPoints
        geo_field = "location"
        fields = "__all__"