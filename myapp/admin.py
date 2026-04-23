from django.contrib import admin
from django.utils import timezone
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from .models import (
    AboutPage,
    HomePage,
    Category,
    Product,
    Brand,
    CartItem,
    ContactInfo,
    # Return Policy Models
    ReturnPolicyHero,
    ReturnFeature,
    ReturnRequirement,
    ReturnException,
    ReturnStep,
    ReturnFAQ,
)

# ==============================
# SIMPLE MODELS
# ==============================
admin.site.register(AboutPage)
admin.site.register(HomePage)
admin.site.register(ContactInfo)
admin.site.register(CartItem)

# ==============================
# BRAND
# ==============================
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {"slug": ("name",)}

# ==============================
# PRODUCT
# ==============================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'category', 'brand', 'price', 'is_new', 'discount',
        'is_flash_sale', 'sold_count_display', 'flash_status_colored', 'best_seller_badge'
    )
    list_filter = ('category', 'brand', 'is_new', 'is_flash_sale')
    search_fields = ('title', 'description')

    # Show total sold count in admin
    def sold_count_display(self, obj):
        sold_count = obj.orderitem_set.aggregate(total=Coalesce(Sum('quantity'), Value(0)))['total']
        return sold_count
    sold_count_display.short_description = 'Sold Count'

    # Show flash status
    def flash_status_colored(self, obj):
        now = timezone.now()
        status = 'N/A'
        try:
            if obj.stock is not None and obj.stock - self.sold_count_display(obj) <= 0:
                status = 'Sold'
            elif obj.flash_start and obj.flash_end:
                if obj.flash_start <= now <= obj.flash_end:
                    status = 'Ongoing'
                elif now < obj.flash_start:
                    status = 'Upcoming'
                else:
                    status = 'Ended'
        except Exception:
            status = 'N/A'
        return status
    flash_status_colored.short_description = 'Flash Sale Status'

    # Best seller badge (optional)
    def best_seller_badge(self, obj):
        sold_count = self.sold_count_display(obj)
        if sold_count >= 10:  # Example threshold for “best seller”
            return "🔥 Best Seller"
        return ""
    best_seller_badge.short_description = 'Best Seller'

# ==============================
# CATEGORY
# ==============================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('parent',)

# ==========================================================
# RETURN POLICY CMS SECTION
# ==========================================================
@admin.register(ReturnPolicyHero)
class ReturnPolicyHeroAdmin(admin.ModelAdmin):
    list_display = ('title', 'days')

@admin.register(ReturnFeature)
class ReturnFeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    list_editable = ('order',)
    ordering = ('order',)

@admin.register(ReturnRequirement)
class ReturnRequirementAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    list_editable = ('order',)
    ordering = ('order',)

@admin.register(ReturnException)
class ReturnExceptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)
    ordering = ('order',)

@admin.register(ReturnStep)
class ReturnStepAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    list_editable = ('order',)
    ordering = ('order',)

@admin.register(ReturnFAQ)
class ReturnFAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order')
    list_editable = ('order',)
    ordering = ('order',)