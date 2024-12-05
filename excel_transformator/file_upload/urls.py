from rest_framework import routers
from django.urls import path, include, re_path

from .views import file_cleaning

router = routers.DefaultRouter()



urlpatterns = [
    path('', include(router.urls)),
    re_path('upload/', file_cleaning, name='file_cleaning')
    ]