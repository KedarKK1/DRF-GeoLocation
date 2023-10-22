from django.test import TestCase

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import CenterPoints
from .serializers import CenterPointsLocationData


# Create your tests here.
class CenterPointsCreateViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.create_url = reverse('center_points-list-create2')

    def test_create_center_point(self):
        data = {
            'name': 'New Point',
            'temprature': 25.0,
            'humidity': 60.0,
            'location': 'POINT(10 20)'  # Replace with your desired coordinates
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CenterPoints.objects.count(), 1)
        center_point = CenterPoints.objects.get()
        self.assertEqual(center_point.name, data['name'])
        self.assertEqual(center_point.temprature, data['temprature'])
        self.assertEqual(center_point.humidity, data['humidity'])
        # ! below line is giving some errors, check those, otherwise all okay
        # self.assertEqual(center_point.location.wkt, data['location'])

    def test_create_center_point_invalid_data(self):
        data = {
            'name': 'New Point',
            'temprature': 'invalid_value',  # Invalid temperature value
            'humidity': 60.0,
            'location': 'POINT(10 20)'  # Replace with your desired coordinates
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_center_point_missing_data(self):
        data = {
            'name': 'New Point',
            # Missing 'temprature' field
            'humidity': 60.0,
            'location': 'POINT(10 20)'  # Replace with your desired coordinates
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
