from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('team/<int:team_id>/fetch_athletes/', views.fetch_athletes, name='fetch_athletes'),
    path('team/<int:team_id>/fetch_depth_chart/', views.fetch_depth_chart, name='fetch_depth_chart'),
]