from django.urls import path
from .views import AdminAnalytics, admin_analytics_export_csv

urlpatterns = [
    path('admin/', AdminAnalytics.as_view(), name='admin_analytics'),
    path('admin/export-csv/', admin_analytics_export_csv, name='admin_analytics_export_csv'),
]