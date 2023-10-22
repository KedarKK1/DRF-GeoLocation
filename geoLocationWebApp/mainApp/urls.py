from django.urls import path
from . import views

urlpatterns = [
    # ^ below ap is for showing leaflet homepage
    path('', views.homePage, name="home"),

    # ^ below api is used for listing all of object queryset -> this is used in leaflet maps
    path('crud/', views.CenterPointsListViewSet.as_view(), name="center_points-list-create"),

    # ^ below api is used for for Creating (1 object), and listing all of object queryset -> used for drf view for creating new point
    path('crud/create', views.CenterPointsCreateViewSet.as_view(), name="center_points-list-create"),

    # ^ below api is used for update(1 object), retrive(1 object) & delete (1 object) via drf view
    path('crud/<int:pk>/', views.CenterPointsUpdateRetriveDeleteSet.as_view(), name="center_points-update-delete-retrive"),
    
    # ^ below api is used for serializing & de-serializing request & response
    path('center_points_api/', views.center_points_api, name="center_points_api"),
]
