from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


def api_root_health(request):
    """
    Health check and entry point returning helpful links to docs and endpoints.
    """
    return JsonResponse({
        'status': 'healthy',
        'project': 'Interview Prep Tracker API',
        'documentation': {
            'swagger': '/api/docs/',
            'redoc': '/api/redoc/',
            'openapi_schema': '/api/schema/',
        },
        'endpoints': {
            'auth_register': '/api/auth/register/',
            'auth_login': '/api/auth/login/',
            'auth_token_refresh': '/api/auth/token/refresh/',
            'auth_me': '/api/auth/me/',
            'problems': '/api/problems/',
            'attempts': '/api/attempts/',
            'stats': '/api/attempts/stats/',
        }
    })


urlpatterns = [
    path('', api_root_health, name='api-root-health'),
    path('admin/', admin.site.urls),

    # Authentication & User Management
    path('api/auth/', include('accounts.urls', namespace='accounts')),

    # Core Tracker Endpoints (Problems, Attempts, Stats)
    path('api/', include('tracker.urls', namespace='tracker')),

    # OpenAPI 3 Schema & Interactive Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
