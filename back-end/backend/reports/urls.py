from django.urls import path, include
from .views import *

urlpatterns = [
    path('get_uni_prod_details', get_uni_prod_details, name='get_uni_prod_details'),
]