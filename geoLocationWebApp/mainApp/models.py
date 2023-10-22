# from django.db import models
from django.contrib.gis.db import models

# Create your models here.

# ^ CenterPoints contains name of city (city, State in string format), latest fetched temprature, humidity and location (latitude, longitude)
class CenterPoints(models.Model):
    name = models.CharField(max_length=50)
    # ! Note - mistakenly i have written temprature instead of temperature as field name, take care while using this field
    temprature = models.FloatField()
    humidity = models.FloatField()
    location = models.PointField()