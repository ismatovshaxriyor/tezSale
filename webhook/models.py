from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class User(models.Model):  
    telegram_id = models.BigIntegerField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.full_name or self.telegram_id}"

class Product(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    original_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    latitude = models.FloatField(max_length=100)
    longitude = models.FloatField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    is_new = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    condition = models.CharField(max_length=50, choices=[('new', 'Yangi'), ('used', 'Ishlatilgan')])
    delivery = models.BooleanField(default=False)
    warranty = models.CharField(max_length=255, null=True, blank=True)

    rating = models.FloatField(default=0)
    reviews = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

def user_directory_path(instance, filename):
    user_id = instance.product.owner.telegram_id  
    return f"ad_images/{user_id}/{filename}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=user_directory_path)
