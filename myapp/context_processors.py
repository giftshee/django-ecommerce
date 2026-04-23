# myapp/context_processors.py

from .models import Category, Wishlist, CartItem

def global_context(request):
    """
    Make top-level categories, wishlist count, and cart count
    available in all templates.
    """
    # Top-level categories
    categories = Category.objects.filter(parent=None).order_by('name')

    # Wishlist and cart counts
    wishlist_count = 0
    cart_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        cart_count = CartItem.objects.filter(user=request.user).count()

    return {
        'categories': categories,
        'wishlist_count': wishlist_count,
        'cart_count': cart_count,
    }
