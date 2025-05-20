from django.urls import path, include
from django.contrib import admin
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Root endpoint
    path('', TemplateView.as_view(template_name='root.html'), name='root'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Endpoints (register/ is now in api/urls.py)
    path('api/', include('api.urls')),
    
    # Authentication
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # Redirect Legacy URLs
    path('accounts/profile/', RedirectView.as_view(url='/api/projects/')),
    path('accounts/login/', RedirectView.as_view(url='/api/auth/login/')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
