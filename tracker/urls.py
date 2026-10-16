from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProblemViewSet, AttemptViewSet

app_name = 'tracker'

router = DefaultRouter()
router.register(r'problems', ProblemViewSet, basename='problem')
router.register(r'attempts', AttemptViewSet, basename='attempt')

urlpatterns = [
    path('', include(router.urls)),
]
