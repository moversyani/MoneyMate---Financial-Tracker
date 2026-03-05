from django.contrib import admin
from .models import Income, Expense

admin.site.register(Income)
admin.site.register(Expense)
admin.site.site_header = "MoneyMate" # Name of the App
admin.site.site_title = "Money Mate Admin Portal" # Title of the Admin Portal
admin.site.index_title = "Welcome to Money Mate"