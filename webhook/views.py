from django.shortcuts import render
from .models import Product

def webapp_test_view(request):
    return render(request, 'webhook_test.html')

def get_products(request):
    products = Product.objects.all().prefetch_related('images').order_by('-created_at')
    return render(request, 'products.html', {'products': products})