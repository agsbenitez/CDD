from django.urls import path
from .views import graph_seno, hello

app_name='graph'
urlpatterns = [
    path('seno/', graph_seno, name="seno"),
    path('hello/', hello, name="hello"),
]