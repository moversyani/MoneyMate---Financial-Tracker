from django.urls import path
from . import views

urlpatterns = [
    # This empty string means the "Home" page
    path('', views.dashboard, name='dashboard'),
]