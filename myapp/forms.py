from django import forms
from .models import Category,Product


# =========================
# Category Form
# =========================

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'parent']  # adjust fields accordingly




# =========================
# Product Create Form
# =========================
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title',
            'category',
            'subcategory',
            'brand',
            'description',
            'price',
            'old_price',
            'color',
            'is_new',
            'discount',
            'image_main',
            'image_hover',
        ]


# =========================
# Product Update Form
# =========================
class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title',
            'category',
            'subcategory',
            'brand',
            'description',
            'price',
            'old_price',
            'color',
            'is_new',
            'discount',
            'image_main',
            'image_hover',
        ]
