from decimal import Decimal
from .models import Product, CartItem
from django.contrib.auth.models import User


class Cart:
    """
    Unified Cart: uses session for anonymous users, DB for logged-in users
    """

    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.user = request.user if request.user.is_authenticated else None

        # For anonymous users, initialize session cart
        if not self.user:
            cart = self.session.get('cart')
            if not cart:
                cart = self.session['cart'] = {}
            self.cart = cart

    # -------------------
    # Add / Update item
    # -------------------
    def add(self, product, quantity=1):
        if self.user:
            # DB cart
            cart_item, created = CartItem.objects.get_or_create(
                user=self.user, product=product
            )
            cart_item.quantity += quantity
            if cart_item.quantity <= 0:
                cart_item.delete()
            else:
                cart_item.save()
        else:
            # Session cart
            product_id = str(product.id)
            if product_id in self.cart:
                self.cart[product_id]['quantity'] += quantity
            else:
                self.cart[product_id] = {'quantity': quantity, 'price': str(product.price)}

            if self.cart[product_id]['quantity'] <= 0:
                self.remove(product_id)

            self.save()

    # -------------------
    # Remove item
    # -------------------
    def remove(self, product_id):
        if self.user:
            CartItem.objects.filter(user=self.user, product_id=product_id).delete()
        else:
            product_id = str(product_id)
            if product_id in self.cart:
                del self.cart[product_id]
                self.save()

    # -------------------
    # Clear cart
    # -------------------
    def clear(self):
        if self.user:
            CartItem.objects.filter(user=self.user).delete()
        else:
            self.session['cart'] = {}
            self.save()

    # -------------------
    # Save session
    # -------------------
    def save(self):
        self.session.modified = True

    # -------------------
    # Get all items
    # -------------------
    def get_items(self):
        if self.user:
            return CartItem.objects.filter(user=self.user)
        else:
            items = []
            for pid, data in self.cart.items():
                try:
                    product = Product.objects.get(id=pid)
                    items.append({
                        'product': product,
                        'quantity': data['quantity'],
                        'total_price': Decimal(data['price']) * data['quantity']
                    })
                except Product.DoesNotExist:
                    continue
            return items

    # -------------------
    # Totals
    # -------------------
    def get_subtotal(self):
        if self.user:
            return sum(item.get_total_price() for item in self.get_items())
        else:
            return sum(item['total_price'] for item in self.get_items())

    def get_shipping(self):
        return Decimal('5.00') if self.get_items() else Decimal('0')

    def get_tax(self):
        return self.get_subtotal() * Decimal('0.10')

    def get_discount(self):
        subtotal = self.get_subtotal()
        return Decimal('5.00') if subtotal > 50 else Decimal('0')

    def get_total(self):
        return self.get_subtotal() + self.get_shipping() + self.get_tax() - self.get_discount()
