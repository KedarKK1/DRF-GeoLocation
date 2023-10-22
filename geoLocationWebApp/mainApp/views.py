from django.shortcuts import render
# from . import models, serializers
from .models import CenterPoints
from .serializers import CenterPointsLocationData
from django.http import JsonResponse
from rest_framework import status, generics
from rest_framework.parsers import JSONParser
# from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import RetrieveUpdateDestroyAPIView
# from rest_framework.viewsets import GenericViewSet
import requests

# ^ handling error pages
def handler400(request, exception):
    context = {"err": "Error 400: Bad Request!", "exception": exception}
    return render(request, "errorPage.html", context)


def handler403(request, exception):
    context = {
        "err": "Error 403: Forbidded (Unauthorized Access)!", "exception": exception}
    return render(request, "errorPage.html", context)


def handler404(request, exception):
    context = {"err": "Error 404! Page not Found!", "exception": exception}
    return render(request, "errorPage.html", context)


def handler500(request,):
    context = {"err": "Error 500! Internal Server Error!"}
    return render(request, "errorPage.html", context)
# handling error pages ends here


# ^ for leaflet-based homepage
def homePage(request):
    return render(request, "homePage.html", {})


# ^ api for serializing & de-serializing request & response
def center_points_api(request):
    if request.method == "GET":
        # get all cordinates
        coordinate_points = CenterPoints.objects.all()
        # print("Coordinate points: {}".format(coordinate_points))
        # de-serialize data for center-points-location-data
        serializer = CenterPointsLocationData(coordinate_points, many=True)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    elif request.method == "POST":
        # parse request & serialize data for center-points-location-data
        data = JSONParser().parse(request)
        serializer = CenterPointsLocationData(data=data)
        if serializer.is_valid():
            serializer.save() # successfully created
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)  # return errors!


# ^ Class based code for Update, Retrieve (1 object), and Delete (1 objects) -> used for update(1 object), retrive(1 object) & delete (1 object)
class CenterPointsUpdateRetriveDeleteSet(RetrieveUpdateDestroyAPIView, CreateModelMixin):
    queryset = CenterPoints.objects.all()
    serializer_class = CenterPointsLocationData

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ^ Class based code for listing all of object queryset -> this is used in leaflet maps
class CenterPointsListViewSet(generics.ListCreateAPIView):
    queryset = CenterPoints.objects.all()
    serializer_class = CenterPointsLocationData

    def list(self, request, *args, **kwargs):
        # Retrieve all CenterPoints instances
        coordinate_points = CenterPoints.objects.all()

        # print("Coordinate points", coordinate_points)
        for coordinate_point in coordinate_points:
            print("Coordinate point", coordinate_point)
            # Extract latitude and longitude
            # Extract latitude and longitude
            latitude = coordinate_point.location.coords[0]
            longitude = coordinate_point.location.coords[1]
            # Make a request to the weather API
            try:
                should_retry = True
                while should_retry:

                    weather_api_url = f"https://api.weather.gov/points/{latitude},{longitude}"
                    # print("weather_api ", weather_api_url)
                    # response = requests.get(weather_api_url, params={"lat": latitude, "lon": longitude})
                    response = requests.get(weather_api_url)

                    if response.status_code == 200:
                        location_data = response.json()

                        # Attempt to get forecast data
                        forecast_url = location_data.get('properties', {}).get('forecast', '')
                        # print("forecast_url ", forecast_url)

                        if forecast_url:
                            forecast_response = requests.get(forecast_url)

                            if forecast_response.status_code == 200:
                                forecast_data = forecast_response.json()
                                # Process the forecast data as needed
                                # print("forecast_data ", forecast_data)
                                # Extract the latest temperature and humidity data
                                latest_period = forecast_data["properties"]["periods"][-1]

                                if "temperature" in latest_period:
                                    temperature = latest_period["temperature"]
                                    temperature_unit = latest_period["temperatureUnit"]
                                else:
                                    temperature = None
                                    temperature_unit = None

                                if "relativeHumidity" in latest_period:
                                    humidity = latest_period["relativeHumidity"]["value"]
                                    humidity_unit = latest_period["relativeHumidity"]["unitCode"]
                                else:
                                    humidity = None
                                    humidity_unit = None

                                # Print the extracted data
                                if temperature is not None and temperature_unit is not None:
                                    # Update the coordinate point model
                                    print("coordinate_point.temprature ", coordinate_point.temprature)
                                    print("temperature ", temperature)
                                    coordinate_point.temprature = temperature

                                if humidity is not None and humidity_unit is not None:
                                    print("coordinate_point.humidity ", coordinate_point.humidity)
                                    print("humidity ", humidity)
                                    coordinate_point.humidity = humidity

                                coordinate_point.save()
                                should_retry = False

                            else:
                                print(
                                    f"Error: Unable to retrieve forecast data - {forecast_response.status_code}")
                                coordinate_point.save()
                                should_retry = False
                        else:
                            print("Error: No forecast URL found in location data")
                            should_retry = False
                        should_retry = False
                    else:
                        print(
                            f"Error: Received a non-200 status code - {response.status_code}", {response})
                        should_retry = False  # Break out of the loop on an unsuccessful request

            except requests.exceptions.RequestException as e:
                print(f"RequestException: {e}")
                return JsonResponse({"error": "Unable to fetch weather data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except ValueError as e:
                print(f"ValueError: {e}")
                return JsonResponse({"error": e}, status=status.HTTP_400_BAD_REQUEST)
            except KeyError as e:
                print(f"KeyError: {e}")
                return JsonResponse({"error": e}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return JsonResponse({"error": e}, status=status.HTTP_400_BAD_REQUEST)

        # deserialize the data
        serializer = CenterPointsLocationData(coordinate_points, many=True)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
        # Make a GET request to the weather API
        # weather_api_url = "https://api.weatherapi.com/"  # Replace with the actual weather API URL
        # response = requests.get(weather_api_url)
        # coordinate_points = CenterPoints.objects.values('location')

        # if response.status_code == 200:
        #     # Deserialize weather data
        #     weather_data = WeatherDataSerializer(data=response.json())

        #     if weather_data.is_valid():
        #         # Create a new CenterPoints object with temperature and humidity data
        #         center_point = CenterPoints(
        #             temperature=weather_data.validated_data['temperature'],
        #             humidity=weather_data.validated_data['humidity']
        #         )
        #         center_point.save()

        #         # Serialize the created object
        #         serializer = CenterPointsLocationData(center_point)

        #         return Response(serializer.data, status=status.HTTP_201_CREATED)
        #     else:
        #         return Response(weather_data.errors, status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     return Response({"error": "Unable to fetch weather data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ^ Class based code for Creating (1 object), and listing all of object queryset -> used for drf view for creating new point
class CenterPointsCreateViewSet(generics.ListCreateAPIView):
    queryset = CenterPoints.objects.all()
    serializer_class = CenterPointsLocationData