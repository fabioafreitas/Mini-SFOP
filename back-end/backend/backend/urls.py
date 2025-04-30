from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views, logout
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.shortcuts import redirect
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="Swagger UI",
        default_version='v1.0',
        description="Mini-SFOP Django Backend",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="fabio.alves.frei@gmail.com"),
    ),
    public=True,  # Allow unauthenticated users to access the schema
    permission_classes=(permissions.AllowAny,),  # Relax permissions for the schema view
)

def redirect_to_login(request):
    logout(request)
    # Always redirect to login, ignoring ?next=
    return redirect('/accounts/login/')

def redirect_to_swagger(_):
    return redirect('/swagger/')

urlpatterns = [
    path('', redirect_to_swagger),
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),    
    path('accounts/logout/', redirect_to_login, name='logout'),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/profile/', redirect_to_swagger),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_jwt'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('llm/', include('llm.urls'), name='llm'),
]
