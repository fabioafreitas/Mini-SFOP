from django.urls import path, include
from .views import *

urlpatterns = [
    path('assign_tasks', assign_tasks, name='assign_tasks'),
    # path('configure_llm', configure_llm, name='configure_llm')
]