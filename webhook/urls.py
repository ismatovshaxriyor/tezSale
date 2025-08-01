from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('all/', views.webapp_test_view, name='webapp_test'),
    path('', views.get_products, name='all_products')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)