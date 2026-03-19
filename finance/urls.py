from django.urls import path
from . import views

urlpatterns = [
    # This empty string means the "Home" page
    path('', views.dashboard, name='dashboard'),
    path('delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('delete-income/<int:pk>/', views.delete_income, name='delete_income'),
]