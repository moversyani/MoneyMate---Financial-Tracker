# finance/urls.py — URL routes for the finance app

from django.urls import path
from . import views

urlpatterns = [
    # Landing page
    path('', views.landing, name='landing'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Finances sidebar pages
    path('income/', views.income_page, name='income_page'),
    path('bills/', views.bills_page, name='bills_page'),

    # Bill and income delete — HTTP_REFERER sends user back to whichever page they came from
    path('delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('delete-income/<int:pk>/', views.delete_income, name='delete_income'),

    # Savings goals
    path('savings/', views.savings_goals, name='savings_goals'),
    path('savings/delete/<int:pk>/', views.delete_goal, name='delete_goal'),

    # Compare & Save pages
    path('compare/insurance/', views.compare_insurance, name='compare_insurance'),
    path('compare/energy/', views.compare_energy, name='compare_energy'),
    path('compare/broadband/', views.compare_broadband, name='compare_broadband'),
    path('compare/home/', views.compare_home, name='compare_home'),

    # Auth routes
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # User pages
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('support/', views.support_view, name='support'),
    # Email verification — token is a UUID passed in the URL
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),

    # Shown after registration — tells user to check their inbox
    path('verify-pending/', views.verify_pending, name='verify_pending'),
]