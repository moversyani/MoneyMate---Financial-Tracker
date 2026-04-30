# finance/urls.py — URL routes for the finance app

from django.urls import path
from . import views

urlpatterns = [
    # Landing page — shown to logged-out users, redirects to dashboard if logged in
    path('', views.landing, name='landing'),

    # Main dashboard — requires login
    path('dashboard/', views.dashboard, name='dashboard'),

    # Bill and income delete routes
    path('delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('delete-income/<int:pk>/', views.delete_income, name='delete_income'),

    # Savings goals
    path('savings/', views.savings_goals, name='savings_goals'),
    path('savings/delete/<int:pk>/', views.delete_goal, name='delete_goal'),

    # Auth routes
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]