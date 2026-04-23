from decimal import Decimal, InvalidOperation
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils import timezone

# =========================
# BRAND & CATEGORY MODELS
# =========================

class Brand(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)  # auto-generate if blank
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories'
    )
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    image_hover = models.ImageField(upload_to='categories/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            i = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce

class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    subcategory = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_products')
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount = models.PositiveIntegerField(null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)  # NEW: stock for sold-out logic
    is_new = models.BooleanField(default=False)
    is_flash_sale = models.BooleanField(default=False)
    flash_start = models.DateTimeField(null=True, blank=True)
    flash_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image_main = models.ImageField(upload_to='products/')
    image_hover = models.ImageField(upload_to='products/', null=True, blank=True)
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    slug = models.SlugField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            i = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def is_flash_active(self):
        now = timezone.now()
        return self.is_flash_sale and self.flash_start and self.flash_end and self.flash_start <= now <= self.flash_end

    @property
    def sold_count(self):
        # Sum all order items quantity for this product
        return self.orderitem_set.aggregate(total=Coalesce(Sum('quantity'), Value(0)))['total']

    @property
    def flash_status(self):
        now = timezone.now()
        if self.stock - self.sold_count <= 0:
            return 'sold'
        if self.is_flash_sale and self.flash_start and self.flash_end:
            if self.flash_start <= now <= self.flash_end:
                return 'ongoing'
            elif now < self.flash_start:
                return 'upcoming'
            else:
                return 'ended'
        return 'none'

    def __str__(self):
        return self.title


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"


# =========================
# CUSTOMER & ORDER MODELS
# =========================

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip = models.CharField(max_length=20)
    country = models.CharField(max_length=2)
    save_address = models.BooleanField(default=False)
    billing_same = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')]
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    shipping_address = models.CharField(max_length=255)
    billing_address = models.CharField(max_length=255, blank=True)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order {self.id} - {self.status}"


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.product:
            self.total_price = self.quantity * self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} × {self.product}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=20, blank=True)
    size = models.CharField(max_length=10, blank=True)

    def get_total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} × {self.product.title}"


# =========================
# CMS MODELS
# =========================

class AboutPage(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    text_block_1 = models.TextField()
    text_block_2 = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    video_thumbnail = models.ImageField(upload_to='about/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "About Page Content"


class Testimonial(models.Model):
    client_name = models.CharField(max_length=255)
    text = models.TextField()
    client_image = models.ImageField(upload_to='testimonials/', blank=True, null=True)

    def __str__(self):
        return self.client_name


class HomePage(models.Model):
    hero_title = models.CharField(max_length=200, blank=True, null=True)
    hero_description = models.TextField(blank=True, null=True)
    featured_product_name = models.CharField(max_length=200, blank=True, null=True)
    featured_product_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    featured_product_original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    featured_product_image = models.ImageField(upload_to='homepage/', blank=True, null=True)
    mini_product_1_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    mini_product_2_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    mini_product_3_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    mini_product_4_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    mini_product_5_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    mini_product_1_image = models.ImageField(upload_to='homepage/', blank=True, null=True)
    mini_product_2_image = models.ImageField(upload_to='homepage/', blank=True, null=True)
    mini_product_3_image = models.ImageField(upload_to='homepage/', blank=True, null=True)
    mini_product_4_image = models.ImageField(upload_to='homepage/', blank=True, null=True)
    mini_product_5_image = models.ImageField(upload_to='homepage/', blank=True, null=True)

    def __str__(self):
        return f"Homepage Content #{self.pk}"

    def clean(self):
        decimal_fields = [
            'featured_product_price',
            'featured_product_original_price',
            'mini_product_1_price',
            'mini_product_2_price',
            'mini_product_3_price',
            'mini_product_4_price',
            'mini_product_5_price',
        ]
        for field in decimal_fields:
            value = getattr(self, field)
            if value in ('', None):
                setattr(self, field, None)
            else:
                try:
                    setattr(self, field, Decimal(value))
                except (InvalidOperation, TypeError, ValueError):
                    raise ValidationError({field: 'Invalid decimal value'})


class ContactInfo(models.Model):
    address = models.CharField(max_length=255)
    email_primary = models.EmailField()
    email_secondary = models.EmailField(blank=True, null=True)
    phone_hours_weekdays = models.CharField(max_length=100)
    phone_hours_weekend = models.CharField(max_length=100)
    google_map_embed_url = models.TextField(help_text="Paste iframe src URL only")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Contact Info"


# =========================
# RETURN POLICY MODELS
# =========================

class ReturnPolicyHero(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    days = models.PositiveIntegerField(default=30)

    def __str__(self):
        return self.title


class ReturnFeature(models.Model):
    icon = models.CharField(max_length=100, help_text="Bootstrap icon class e.g. bi-shield-check")
    title = models.CharField(max_length=150)
    description = models.TextField()
    link = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class ReturnRequirement(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class ReturnException(models.Model):
    name = models.CharField(max_length=150)
    icon = models.CharField(max_length=100, default="bi-tag")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class ReturnStep(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class ReturnFAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question


# =========================
# CHAT & SUPPORT MODELS
# =========================

class ChatMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}: {self.message[:20]}"


class SupportMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_answered = models.BooleanField(default=False)
    reply = models.TextField(blank=True, null=True)
    read_by_user = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.created_at}"