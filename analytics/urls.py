from django.urls import path
from .views import AdminAnalytics

urlpatterns = [
    path('admin/', AdminAnalytics.as_view(), name='admin_analytics'),
]