from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Настройка DRF YASG для документации
schema_view = get_schema_view(
   openapi.Info(
      title="Habit Tracker API",
      default_version='v1',
      description="API для трекера привычек, разработанного по мотивам книги 'Атомные привычки'",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    # Эндпоинты Djoser для регистрации/авторизации (JWT)
    path('users/', include('djoser.urls')),
    path('users/', include('djoser.urls.jwt')),
    # Эндпоинты для привычек
    path('habits/', include('habits.urls')),
    
    # Документация (Swagger)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
