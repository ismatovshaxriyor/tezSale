from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    def create_user(self, phone_number, telegram_id=None, full_name="", password=None):
        if not phone_number:
            raise ValueError('Telefon raqami majburiy')
        
        user = self.model(
            phone_number=phone_number,
            telegram_id=telegram_id,
            full_name=full_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, telegram_id=None, full_name="", password=None):
        user = self.create_user(
            phone_number=phone_number,
            telegram_id=telegram_id,
            full_name=full_name,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    # Sizning original fieldlaringiz - sayt uchun moslashtirilgan
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(
        max_length=20, 
        unique=True,  # Login uchun unique bo'lishi kerak
        help_text='Login uchun telefon raqami. +998901234567 formatda'
    )
    
    # Sayt uchun qo'shimcha field (ixtiyoriy)
    username = models.CharField(
        max_length=150, 
        null=True, 
        blank=True,
        help_text='Ixtiyoriy username field'
    )
    
    # Django auth uchun minimal kerakli fieldlar
    
    # USER STATUS FIELDLARI
    is_active = models.BooleanField(
        default=True,
        help_text='User faolmi? False bo\'lsa login qila olmaydi, soft delete uchun ishlatiladi'
    )
    
    is_staff = models.BooleanField(
        default=False,
        help_text='Django admin panelga kirish huquqi. True bo\'lsa admin paneldan foydalana oladi'
    )
    
    is_superuser = models.BooleanField(
        default=False,
        help_text='Barcha ruxsatlarga ega. True bo\'lsa hech qanday cheklovsiz admin huquqlari'
    )
    
    # VAQT VA SANA FIELDLARI
    date_joined = models.DateTimeField(
        auto_now_add=True,
        help_text='User ro\'yxatdan o\'tgan sana-vaqt. Avtomatik o\'rnatiladi'
    )
    
    last_login = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='Oxirgi marta login qilgan vaqt. Django avtomatik yangilaydi'
    )
    
    # EMAIL FIELD (ixtiyoriy, lekin ko'pincha kerak bo'ladi)
    email = models.EmailField(
        null=True, 
        blank=True,
        help_text='User emaili, notification va password reset uchun ishlatiladi'
    )
    
    # PASSWORD FIELD (AbstractBaseUser dan meros qilib olinadi, lekin tushuntirish uchun)
    # password = models.CharField(max_length=128) - bu AbstractBaseUser da bor
    
    # PERMISSION FIELDLARI (PermissionsMixin dan keladi)
    # groups = models.ManyToManyField(Group) - Permission guruhlari
    # user_permissions = models.ManyToManyField(Permission) - Individual ruxsatlar
    
    objects = UserManager()
    
    USERNAME_FIELD = 'phone_number'  # Login uchun phone_number ishlatiladi
    REQUIRED_FIELDS = []  # Superuser yaratishda qo'shimcha so'raladigan fieldlar
    
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
