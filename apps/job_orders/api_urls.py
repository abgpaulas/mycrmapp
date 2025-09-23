from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
# Register viewsets here

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard-stats/', api_views.dashboard_stats, name='dashboard_stats'),
]
