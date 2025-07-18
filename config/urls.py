from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view



class JWTSchemaGenerator(OpenAPISchemaGenerator):
    def get_security_definitions(self):
        security_definitions = super().get_security_definitions()
        security_definitions['Bearer'] = {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
        return security_definitions

schema_view = get_schema_view(
    openapi.Info(
        title='API Products',
        default_version='v1',
        description='sssss',
        terms_of_service='google.com',
        contact=openapi.Contact('shaxriyorismatov2007@gmail.com'),
        license=openapi.License(name='BSD License')
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhook/', include('webhook.urls')), 
    path('api/v1/', include('api.urls')),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('', schema_view.with_ui('swagger' ,cache_timeout=0), name='schema-swaggeer-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
]
