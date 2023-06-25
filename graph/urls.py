from django.urls import path
from .views import graph, cap, signals, ante, dist

app_name='graph'
urlpatterns = [
    path('graf/', graph, name="graf"),
    path('cap/', cap, name="cap"),
    path('signals', signals, name="signals"),
    path('antenas', ante, name='ante'),
    path('destancia', dist, name='dist')
]