from decimal import Decimal, InvalidOperation
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .cart import Cart
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from .models import (
    AboutPage, HomePage, Product, CartItem, ContactInfo, Customer,
    Order, OrderItem, Category, Brand,Wishlist
)
from .forms import CategoryForm, ProductForm
from django.core.paginator import Paginator
from .forms import ProductForm
from django.http import QueryDict
from .models import AboutPage, Testimonial
from django.contrib import messages
from decimal import Decimal, InvalidOperation


def safe_decimal(value):
    try:
        if value in (None, ''):
            return None
        return Decimal(value)
    except (TypeError, InvalidOperation):
        return None
def search(request):
    query = request.GET.get('q', '').strip()

    if query:
        results = Product.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__name__icontains=query)
        ).distinct()
    else:
        results = Product.objects.none()

    return render(request, 'search.html', {
        'query': query,
        'results': results,
        'results_count': results.count(),
    })
# @login_required
from django.utils import timezone
from django.db.models import Sum
from .models import HomePage, Product

def safe_decimal(value):
    try:
        return Decimal(value)
    except (TypeError, ValueError, InvalidOperation):
        return None  # or 0, depending on your logic


from decimal import Decimal
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from .models import HomePage, Product

def safe_decimal(value):
    try:
        return Decimal(value)
    except:
        return None
from decimal import Decimal
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from .models import HomePage, Product

def safe_decimal(value):
    try:
        return Decimal(value)
    except:
        return Decimal('0')

from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce

from .models import HomePage, Product
from .utils import safe_decimal  # Your helper function


def home(request):
    content = HomePage.objects.first()
    now = timezone.now()

    # ==========================
    # HANDLE POST REQUESTS FOR HOMEPAGE CONTENT
    # ==========================
    if request.method == 'POST':
        # --------------------------
        # CREATE HOMEPAGE CONTENT
        # --------------------------
        if 'create_content' in request.POST:
            HomePage.objects.all().delete()
            content = HomePage.objects.create(
                hero_title='New Hero Title',
                hero_description='New Hero Description',
                featured_product_name='Sample Product',
                featured_product_price=Decimal('100'),
                featured_product_original_price=Decimal('150'),
                mini_product_1_price=Decimal('50'),
                mini_product_2_price=Decimal('60'),
                mini_product_3_price=Decimal('70'),
                mini_product_4_price=Decimal('80'),
                mini_product_5_price=Decimal('90'),
            )
            messages.success(request, "New homepage content created.")
            return redirect('myapp:index')

        # --------------------------
        # DELETE HOMEPAGE CONTENT
        # --------------------------
        if 'delete_content' in request.POST and content:
            content.delete()
            messages.success(request, "Homepage content deleted.")
            return redirect('myapp:index')

        # --------------------------
        # UPDATE HOMEPAGE CONTENT
        # --------------------------
        if content:
            content.hero_title = request.POST.get('hero_title')
            content.hero_description = request.POST.get('hero_description')
            content.featured_product_name = request.POST.get('featured_product_name')
            content.featured_product_price = safe_decimal(request.POST.get('featured_product_price'))
            content.featured_product_original_price = safe_decimal(request.POST.get('featured_product_original_price'))

            # Hero background image
            if request.POST.get('delete_hero_background') and content.hero_background:
                content.hero_background.delete(save=False)
                content.hero_background = None
            uploaded_hero = request.FILES.get('hero_background')
            if uploaded_hero:
                content.hero_background = uploaded_hero

            # Featured product image
            if request.POST.get('delete_featured_image') and content.featured_product_image:
                content.featured_product_image.delete(save=False)
                content.featured_product_image = None
            uploaded_featured = request.FILES.get('featured_product_image')
            if uploaded_featured:
                content.featured_product_image = uploaded_featured

            # Mini products 1–5
            for i in range(1, 6):
                price_field = f'mini_product_{i}_price'
                setattr(content, price_field, safe_decimal(request.POST.get(price_field)))

                image_field = f'mini_product_{i}_image'
                if request.POST.get(f'delete_mini_product_{i}_image'):
                    image_instance = getattr(content, image_field)
                    if image_instance:
                        image_instance.delete(save=False)
                    setattr(content, image_field, None)
                uploaded = request.FILES.get(image_field)
                if uploaded:
                    setattr(content, image_field, uploaded)

            content.save()
            messages.success(request, "Homepage content updated.")
            return redirect('myapp:index')

    # ==========================
    # FETCH POPULAR DEALS (MINI PRODUCTS)
    # ==========================
    mini_products = []
    if content:
        for i in range(1, 6):
            image = getattr(content, f'mini_product_{i}_image', None)
            price = getattr(content, f'mini_product_{i}_price', None)
            if image:
                mini_products.append({'image': image, 'price': price})

    # ==========================
    # FETCH FLASH SALE PRODUCTS
    # ==========================
    flash_products = []
    all_flash_products = Product.objects.filter(is_flash_sale=True).order_by('flash_start')

    for product in all_flash_products:
        # Make timezone-aware
        if product.flash_start and timezone.is_naive(product.flash_start):
            product.flash_start = timezone.make_aware(product.flash_start)
        if product.flash_end and timezone.is_naive(product.flash_end):
            product.flash_end = timezone.make_aware(product.flash_end)

        # Determine flash status
        now = timezone.now()
        if product.stock and product.sold_count >= product.stock:
            product.flash_status_resolved = 'sold'
        elif product.is_flash_sale and product.flash_start and product.flash_end:
            if now < product.flash_start:
                product.flash_status_resolved = 'upcoming'
            elif product.flash_start <= now <= product.flash_end:
                product.flash_status_resolved = 'ongoing'
            else:
                product.flash_status_resolved = 'ended'
        else:
            product.flash_status_resolved = 'none'

        flash_products.append(product)

    # ==========================
    # FETCH BEST SELLERS
    # ==========================
    best_sellers = Product.objects.annotate(
        total_sold=Coalesce(Sum('orderitem__quantity'), Value(0))
    ).order_by('-total_sold')[:8]

    # ==========================
    # RENDER TEMPLATE
    # ==========================
    context = {
        'content': content,
        'mini_products': mini_products,
        'flash_products': flash_products,
        'best_sellers': best_sellers,
        'now': now,
    }

    return render(request, 'index.html', context)
def contact_page(request):
    contact = ContactInfo.objects.first()  # Assuming there's only one row

    if request.method == 'POST':
        # Retrieve form fields
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # TODO: Add saving or sending email logic here
        # For example: save to DB or send email

        messages.success(request, "Your message has been sent successfully!")
        return redirect('myapp:contact')  # Make sure your URL is named 'contact'

    return render(request, 'contact.html', {'contact': contact})
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


# myapp/views.py

def about(request):
    """View for About page with admin controls for About and Testimonials"""

    # Fetch About content (assume only one instance)
    about = AboutPage.objects.first()
    testimonials = Testimonial.objects.all()

    # Handle POST requests for staff users
    if request.method == "POST" and request.user.is_staff:

        # ----- ABOUT SECTION -----
        if request.POST.get("create_about"):
            AboutPage.objects.create(
                title="Your Title Here",
                description="Description here",
                text_block_1="Text block 1",
                text_block_2="Text block 2"
            )
            messages.success(request, "About content created successfully!")
            return redirect('myapp:about')

        if request.POST.get("delete_about") and about:
            about.delete()
            messages.success(request, "About content deleted successfully!")
            return redirect('myapp:about')

        if any(field in request.POST for field in [
            "title", "description", "text_block_1", "text_block_2", "video_url"
        ]) and about:
            about.title = request.POST.get("title", about.title)
            about.description = request.POST.get("description", about.description)
            about.text_block_1 = request.POST.get("text_block_1", about.text_block_1)
            about.text_block_2 = request.POST.get("text_block_2", about.text_block_2)
            about.video_url = request.POST.get("video_url", about.video_url)

            if request.FILES.get("video_thumbnail"):
                about.video_thumbnail = request.FILES.get("video_thumbnail")

            about.save()
            messages.success(request, "About content updated successfully!")
            return redirect('myapp:about')

        # ----- TESTIMONIALS SECTION -----
        if request.POST.get("delete_testimonial"):
            testimonial_id = request.POST.get("delete_testimonial")
            testimonial = get_object_or_404(Testimonial, id=testimonial_id)
            testimonial.delete()
            messages.success(request, "Testimonial deleted successfully!")
            return redirect('myapp:about')

        if any(field in request.POST for field in ["client_name", "testimonial_text"]):
            testimonial_id = request.POST.get("testimonial_id")

            if testimonial_id:
                testimonial = get_object_or_404(Testimonial, id=testimonial_id)
                msg_text = "Testimonial updated successfully!"
            else:
                testimonial = Testimonial()
                msg_text = "Testimonial added successfully!"

            testimonial.client_name = request.POST.get("client_name")
            testimonial.text = request.POST.get("testimonial_text")

            if request.FILES.get("client_image"):
                testimonial.client_image = request.FILES.get("client_image")

            testimonial.save()
            messages.success(request, msg_text)
            return redirect('myapp:about')

    # ✅ THIS IS THE MISSING PART (handles GET requests)
    return render(request, "about.html", {
        "about": about,
        "testimonials": testimonials,
    })
    # views.py
@staff_member_required
def edit_about(request, pk):
    about = get_object_or_404(About, pk=pk)
    if request.method == "POST":
        about.title = request.POST.get('title', about.title)
        about.description = request.POST.get('description', about.description)
        about.text_block_1 = request.POST.get('text_block_1', about.text_block_1)
        about.text_block_2 = request.POST.get('text_block_2', about.text_block_2)
        about.video_url = request.POST.get('video_url', about.video_url)
        if request.FILES.get('video_thumbnail'):
            about.video_thumbnail = request.FILES.get('video_thumbnail')
        about.save()
        messages.success(request, "About content updated successfully!")
        return redirect('myapp:about')
    return render(request, 'about.html', {'about': about}) 
from .models import Wishlist

@login_required(login_url='login')  # change if your login URL is different
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'myapp/wishlist.html', {
        'wishlist_items': wishlist_items
    })
@login_required
def wishlist_add(request, product_id):
    """Add/remove a product to/from user's wishlist."""
    product = get_object_or_404(Product, pk=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        # Already exists → remove from wishlist
        wishlist_item.delete()

    return redirect(request.META.get('HTTP_REFERER', 'myapp:product_list'))


    return redirect('myapp:wishlist')
def remove_from_wishlist(request, product_id):
    if request.user.is_authenticated:
        Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    else:
        wishlist = request.session.get('wishlist', [])
        if product_id in wishlist:
            wishlist.remove(product_id)
            request.session['wishlist'] = wishlist

    return redirect('myapp:wishlist')
@login_required
def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    wishlist_item.delete()
    return redirect('myapp:wishlist')

def remove_from_session_wishlist(request, item_id):
    # If you have session-based wishlist for anonymous users
    wishlist = request.session.get('wishlist', [])
    if item_id in wishlist:
        wishlist.remove(item_id)
        request.session['wishlist'] = wishlist
    return redirect('myapp:wishlist')


def wishlist_count(request):
    if request.user.is_authenticated:
        count = Wishlist.objects.filter(user=request.user).count()
    else:
        count = len(request.session.get('wishlist', []))
    return {'wishlist_count': count}
from django.contrib.auth.decorators import login_required
from myapp.models import Product, CartItem
from django.db.models import F, Sum

# -------------------------
# CART DETAIL
# -------------------------

@login_required
def cart_detail(request):
    """
    Display all items in the user's cart along with totals.
    """
    cart_items = CartItem.objects.filter(user=request.user)

    # Calculate subtotal
    cart_subtotal = cart_items.aggregate(
        subtotal=Sum(F('quantity') * F('product__price'))
    )['subtotal'] or Decimal('0.00')

    # Optional: Tax, shipping, discount
    shipping_cost = Decimal('100.00')  # make it Decimal too
    tax_rate = Decimal('0.16')          # 16% VAT
    tax = cart_subtotal * tax_rate
    discount = Decimal('0.00')          # implement your own logic
    cart_total = cart_subtotal + shipping_cost + tax - discount

    context = {
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
        'shipping_cost': shipping_cost,
        'tax': tax,
        'discount': discount,
        'cart_total': cart_total,
    }

    return render(request, 'cart.html', context)



# -------------------------
# ADD TO CART
# -------------------------
@login_required
def add_to_cart(request, product_id):
    """
    Add a product to the cart or increase quantity if already exists.
    """
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get('quantity', 1))

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return redirect('myapp:cart_detail')
# -------------------------
# REMOVE FROM CART
# -------------------------
@login_required
@login_required
def remove_from_cart(request, product_id):
    """
    Remove a product from the user's cart.
    """
    cart_item = get_object_or_404(CartItem, user=request.user, product__pk=product_id)
    cart_item.delete()
    return redirect('myapp:cart_detail')



# -------------------------
# CLEAR CART
# -------------------------
@login_required
def clear_cart(request):
    """
    Remove all items from the user's cart.
    """
    CartItem.objects.filter(user=request.user).delete()
    return redirect('myapp:cart_detail')


# -------------------------
# UPDATE QUANTITY
# -------------------------
@login_required
def update_quantity(request, product_id):
    """
    Update the quantity of a product in the cart.
    Supports:
    - Increase
    - Decrease
    - Manual input
    """
    # Get the cart item for the logged-in user and given product
    cart_item = get_object_or_404(CartItem, user=request.user, product__pk=product_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            # Manual input from the quantity field
            try:
                qty = int(request.POST.get('quantity', cart_item.quantity))
                if qty > 0:
                    cart_item.quantity = qty
            except (ValueError, TypeError):
                pass

        cart_item.save()

    return redirect('myapp:cart_detail')
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Customer, Order, OrderItem
from .cart import Cart, CartItem
from .mpesa import lipa_na_mpesa  # your M-Pesa integration function


@login_required
@require_http_methods(["GET", "POST"])
def checkout(request):
    cart = Cart(request)

    # Prevent checkout if cart is empty
    if request.method == "GET" and not cart.get_items():
        messages.warning(request, "Your cart is empty.")
        return redirect('myapp:cart_detail')

    if request.method == "POST":
        data = request.POST

        # -----------------------------
        # Validate required fields
        # -----------------------------
        required_fields = [
            'first_name', 'last_name', 'email',
            'phone', 'address', 'city', 'state', 'zip', 'country'
        ]

        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            messages.error(
                request,
                f"Please fill all required fields: {', '.join(missing_fields)}"
            )
            return redirect('myapp:checkout')

        # -----------------------------
        # CUSTOMER
        # -----------------------------
        customer, created = Customer.objects.get_or_create(
            email=data.get('email'),
            defaults={'user': request.user}
        )
        if not customer.user:
            customer.user = request.user

        customer.first_name = data.get('first_name')
        customer.last_name = data.get('last_name')
        customer.phone = data.get('phone')
        customer.address = data.get('address')
        customer.apartment = data.get('apartment') or ''
        customer.city = data.get('city')
        customer.state = data.get('state')
        customer.zip = data.get('zip')
        customer.country = data.get('country')
        customer.save_address = 'save_address' in data
        customer.billing_same = 'billing_same' in data
        customer.save()

        # -----------------------------
        # ORDER TOTALS
        # -----------------------------
        subtotal = cart.get_subtotal()
        tax = cart.get_tax()
        shipping = cart.get_shipping()
        total = cart.get_total()

        # -----------------------------
        # CREATE ORDER
        # -----------------------------
        order = Order.objects.create(
            customer=customer,
            payment_method=data.get('payment_method'),
            shipping_address=f"{customer.address}, {customer.city}, {customer.state}, {customer.zip}, {customer.country}",
            billing_address=f"{customer.address}, {customer.city}, {customer.state}, {customer.zip}, {customer.country}"
            if customer.billing_same else "",
            subtotal=subtotal,
            tax=tax,
            shipping_fee=shipping,
            total=total,
        )

        # -----------------------------
        # CREATE ORDER ITEMS
        # -----------------------------
        for item in cart.get_items():
            if isinstance(item, CartItem):
                product = item.product
                quantity = item.quantity
                color = item.color
                size = item.size
            else:  # session-based cart
                product = item['product']
                quantity = item['quantity']
                color = item.get('color', '')
                size = item.get('size', '')

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                color=color,
                size=size,
                total_price=product.price * quantity
            )

        # -----------------------------
        # PAYMENT HANDLING
        # -----------------------------
        payment_method = data.get('payment_method')

        if payment_method == "mpesa":
            phone_number = data.get('mpesa_number')
            if not phone_number:
                messages.error(request, "Please provide a phone number for M-Pesa payment.")
                return redirect('myapp:checkout')

            response = lipa_na_mpesa(
                phone_number=phone_number,
                amount=int(total),
                account_reference=f"Order{order.id}",
                transaction_desc="Order Payment"
            )

            if response.get("ResponseCode") == "0":
                messages.success(
                    request,
                    "M-Pesa payment request sent! Check your phone to complete payment."
                )
                cart.clear()
                return redirect('myapp:order_confirmation', order_id=order.id)
            else:
                messages.error(
                    request,
                    f"Failed to initiate M-Pesa payment: {response.get('errorMessage', 'Unknown error')}"
                )
                return redirect('myapp:checkout')

        # Other payment methods (credit_card / cash)
        cart.clear()
        messages.success(request, "Order placed successfully!")
        return redirect('myapp:order_confirmation', order_id=order.id)

    # -----------------------------
    # GET REQUEST
    # -----------------------------
    customer = None
    if request.user.is_authenticated:
        customer = Customer.objects.filter(user=request.user).first()

    context = {
        'customer': customer,
        'cart_items': cart.get_items(),
        'subtotal': cart.get_subtotal(),
        'shipping': cart.get_shipping(),
        'tax': cart.get_tax(),
        'total': cart.get_total(),
        'payment_method': 'credit_card',
    }

    return render(request, 'checkout.html', context)





import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Order

@csrf_exempt
def mpesa_callback(request):
    """
    Handle Daraja STK push callback.
    """
    if request.method != "POST":
        return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid method"}, status=400)

    try:
        data = json.loads(request.body)
        stk_callback = data.get("Body", {}).get("stkCallback", {})
        result_code = stk_callback.get("ResultCode")
        callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])

        # Extract needed fields safely
        amount = next((item["Value"] for item in callback_metadata if item["Name"] == "Amount"), None)
        phone = next((item["Value"] for item in callback_metadata if item["Name"] == "PhoneNumber"), None)
        receipt_number = next((item["Value"] for item in callback_metadata if item["Name"] == "MpesaReceiptNumber"), None)
        account_reference = next((item["Value"] for item in callback_metadata if item["Name"] in ["BillRefNumber", "AccountReference"]), None)

        # Find order
        order = None
        if account_reference and account_reference.startswith("Order"):
            order_id = int(account_reference.replace("Order", ""))
            order = Order.objects.filter(id=order_id).first()

        if order:
            if result_code == 0:
                order.status = "paid"
                order.mpesa_receipt_number = receipt_number
                order.complete = True
            else:
                order.status = "failed"
            order.save()

    except Exception as e:
        print("Error processing M-Pesa callback:", e)
        return JsonResponse({"ResultCode": 1, "ResultDesc": "Error"}, status=500)

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"}, status=200)

def add_brand(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()

        if not name:
            messages.error(request, "Name field is required.")
            return render(request, 'add_brand.html', {'name': name, 'description': description})

        # Optionally, check if brand with this name already exists
        if Brand.objects.filter(name=name).exists():
            messages.error(request, "Brand with this name already exists.")
            return render(request, 'add_brand.html', {'name': name, 'description': description})

        # Create and save the new brand
        brand = Brand(name=name, description=description)
        brand.save()

        messages.success(request, "Brand added successfully.")
        return redirect('myapp:category')
    return render(request, 'add_brand.html')

def is_admin(user):
    return user.is_staff

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category, Brand, Wishlist

def category(request, slug=None):
    products = Product.objects.select_related('category', 'brand').all()
    categories = Category.objects.filter(parent=None)
    brands = Brand.objects.all()
    selected_category = None

    # --- Filter by slug if provided ---
    if slug:
        selected_category = get_object_or_404(Category, slug=slug)
        subcategories = selected_category.subcategories.all()
        products = products.filter(Q(category=selected_category) | Q(category__in=subcategories))

    # --- Search ---
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(title__icontains=search_query)

    # --- Brands ---
    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        products = products.filter(brand__id__in=selected_brands)

    # --- Price ---
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    # --- Sorting ---
    sort_option = request.GET.get('sort')
    if sort_option == 'price_asc':
        products = products.order_by('price')
    elif sort_option == 'price_desc':
        products = products.order_by('-price')
    elif sort_option == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-created_at')  # default

    # --- Pagination ---
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    # Preserve GET params
    get_params = request.GET.copy()
    if 'page' in get_params:
        get_params.pop('page')
    query_string = get_params.urlencode()

    context = {
        'products': products_page,
        'categories': categories,
        'brands': brands,
        'selected_category': selected_category,
        'selected_brands': selected_brands,
        'search_query': search_query,
        'selected_sort': sort_option,
        'price_min': price_min or '',
        'price_max': price_max or '',
        'query_string': query_string,
    }

    return render(request, 'category.html', context)


def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'myapp/wishlist.html', {'wishlist_items': wishlist_items})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'myapp/product_list.html', {'products': products})

def product_list_view(request):
    products = Product.objects.all()
    categories = Category.objects.filter(parent=None)
    brands = Brand.objects.all()

    search_query = request.GET.get('q', '')
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Category
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Price
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        try:
            products = products.filter(price__gte=float(price_min))
        except ValueError:
            pass
    if price_max:
        try:
            products = products.filter(price__lte=float(price_max))
        except ValueError:
            pass

    # Brands
    brands_filter = request.GET.getlist('brand')
    if brands_filter:
        products = products.filter(brand__id__in=brands_filter)

    # Colors
    colors_filter = request.GET.getlist('colors')
    if colors_filter:
        products = products.filter(colors__overlap=colors_filter)

    # Sorting
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')

    # Pagination
    items_per_page = request.GET.get('items_per_page') or 12
    try:
        items_per_page = int(items_per_page)
    except ValueError:
        items_per_page = 12

    paginator = Paginator(products, items_per_page)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    # Colors for sidebar filter (from filtered products)
    colors = set()
    for p in products:
        for c in p.colors:
            colors.add(c)

    context = {
        'products': products_page,
        'categories': categories,
        'brands': brands,
        'colors': colors,
        'search_query': search_query,
        'selected_brands': brands_filter,
        'price_min': price_min,
        'price_max': price_max,
        'selected_sort': sort,
        'query_string': request.GET.urlencode(),
    }

    return render(request, 'product_list.html', context)
@login_required
@user_passes_test(is_admin)
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully.")
            return redirect('myapp:category_products', category_id=form.instance.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CategoryForm()
    items_per_page_options = [12, 24, 48, 96]
    return render(request, 'category.html', {
        'category_form': form,
        'items_per_page_options': items_per_page_options,
    })
@login_required
@user_passes_test(is_admin)
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            category.name = name
            category.save()
            return redirect('category_list')
    return render(request, 'edit_category.html', {'category': category})
@login_required
@user_passes_test(is_admin)
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'confirm_delete.html', {'object': category, 'type': 'Category'})

@login_required
@user_passes_test(is_admin)
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.title}' added successfully.")
            return redirect('myapp:category_products', category_id=product.category.id)
        else:
            category_id = request.POST.get('category')
            category = get_object_or_404(Category, pk=category_id) if category_id else None
            products = Product.objects.filter(category=category) if category else Product.objects.none()
            categories = Category.objects.prefetch_related('children').all()
            category_form = CategoryForm()
            brands = Brand.objects.all()
            colors = Product.objects.values_list('color', flat=True).distinct()
            items_per_page_options = [12, 24, 48, 96]

            messages.error(request, "Please fix the errors in the product form.")
            return render(request, 'category.html', {
                'category': category,
                'products': products,
                'add_product_form': form,
                'category_form': category_form,
                'categories': categories,
                'brands': brands,
                'colors': colors,
                'items_per_page_options': items_per_page_options,
            })
    else:
        return redirect('myapp:category')

@login_required
@user_passes_test(is_admin)
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # ✅ request.FILES is correct
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect('myapp:product_list')  # or category page if needed
    else:
        form = ProductForm()

    return render(request, 'myapp/product_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)  # ✅
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('myapp:product_list')  # redirect to product list or category view
    else:
        form = ProductForm(instance=product)

    return render(request, 'myapp/product_form.html', {  # render same template as add
        'form': form,
        'edit_mode': True,
        'product_to_edit': product,
    })

@login_required
@user_passes_test(is_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f'Product "{product.title}" has been deleted.')
        return redirect('myapp:category')
    return render(request, 'product_confirm_delete.html', {'product': product})
@login_required
@staff_member_required
def subcategory_add(request, category_id):
    parent_category = get_object_or_404(Category, id=category_id, parent__isnull=True)

    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image') if hasattr(Category, 'image') else None

        if name:
            Category.objects.create(name=name, parent=parent_category, image=image)
            messages.success(request, "Subcategory added successfully.")
            return redirect('myapp:category_products', category_id=parent_category.id)
        else:
            messages.error(request, "Name is required.")

    return render(request, 'myapp/category.html', {'category': parent_category})
@login_required
@staff_member_required
def subcategory_update(request, pk):
    subcategory = get_object_or_404(Category, pk=pk, parent__isnull=False)

    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image') if hasattr(Category, 'image') else None

        if name:
            subcategory.name = name
            if image:
                subcategory.image = image
            subcategory.save()
            messages.success(request, "Subcategory updated successfully.")
            return redirect('myapp:category_products', category_id=subcategory.parent.id)
        else:
            messages.error(request, "Name is required.")

    return render(request, 'myapp/update_subcategory.html', {'subcategory': subcategory})
@login_required
@staff_member_required
def subcategory_delete(request, pk):
    subcategory = get_object_or_404(Category, pk=pk, parent__isnull=False)
    parent_id = subcategory.parent.id

    if request.method == 'POST':
        subcategory.delete()
        messages.success(request, "Subcategory deleted successfully.")
        return redirect('myapp:category_products', category_id=parent_id)

    return render(request, 'myapp/confirm_delete.html', {
        'object': subcategory,
        'type': 'Subcategory'
    })




def faq(request):
    return render(request, 'faq.html')
def account_view(request):
    return render(request, 'account.html')



def account(request):
    return render(request, 'account.html')



from django.shortcuts import render, get_object_or_404, redirect
from .models import Order, Product, Customer

def order_confirmation(request, order_id=None):
    # Ensure the user is logged in
    if not request.user.is_authenticated:
        return redirect('myapp:index')

    # Get or create Customer instance for this user
    customer, created = Customer.objects.get_or_create(
        user=request.user,
        defaults={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
    )

    # Get the order
    if order_id:
        # Specific order
        order = get_object_or_404(Order, id=order_id, customer=customer)
    else:
        # Latest order for this customer
        order = Order.objects.filter(customer=customer).last()
        if not order:
            return render(request, 'myapp/no_order.html')  # No orders yet

    # Calculate subtotal and total
    subtotal = sum(item.quantity * item.product.price for item in order.items.all())
    order.subtotal = subtotal
    order.total = order.subtotal + getattr(order, 'shipping_fee', 0) + getattr(order, 'tax', 0)
    order.save()

    # Recommended products
    recommended_products = Product.objects.order_by('?')[:3]

    context = {
        'order': order,
        'order_items': order.items.all(),
        'recommended_products': recommended_products,
    }
    return render(request, 'myapp/order_confirmation.html', context)
def privacy(request):
    return render(request, 'privacy.html')

from django.shortcuts import render
from .models import (
    ReturnPolicyHero,
    ReturnFeature,
    ReturnRequirement,
    ReturnException,
    ReturnStep,
    ReturnFAQ
)


def return_policy(request):
    context = {
        "hero": ReturnPolicyHero.objects.first(),
        "features": ReturnFeature.objects.all(),
        "requirements": ReturnRequirement.objects.all(),
        "exceptions": ReturnException.objects.all(),
        "steps": ReturnStep.objects.all(),
        "faqs": ReturnFAQ.objects.all(),
    }

    return render(request, "return_policy.html", context)

def tos(request):
    return render(request, 'tos.html')

def payment_methods(request):
    return render(request, 'payment-methods.html')
def order_success(request):
    return render(request, 'order_success.html')
from .models import ReturnFAQ

def support_page(request):
    # Quick actions for support
    quick_actions = [
        {
            "title": "Live Chat",
            "description": "Chat with our support team in real-time",
            "button_text": "Start Chat",
            "type": "chat",  # used by template
            "icon": "bi-chat-dots"
        },
        {
            "title": "Email Support",
            "description": "Send us an email and we’ll get back to you",
            "button_text": "Send Email",
            "type": "email",
            "link": "alicha3033@gmail.com",  # replace with your support email
            "icon": "bi-envelope"
        },
        {
            "title": "Call Us",
            "description": "Reach us by phone for immediate help",
            "button_text": "Call Now",
            "type": "phone",
            "link": "+254 700670908",  # replace with your support number
            "icon": "bi-telephone"
        },
        {
            "title": "Help Center",
            "description": "Visit our help articles",
            "button_text": "View Articles",
            "type": "link",
            "link": "/help-center/",
            "icon": "bi-book"
        },
    ]

    # Example self-help resources
    self_help_resources = [
        {
            "title": "FAQ",
            "description": "Find answers to frequently asked questions",
            "link": "/faq/",
            "icon": "bi-question-circle"
        },
        {
            "title": "Order Tracking",
            "description": "Check the status of your orders",
            "link": "/orders/",
            "icon": "bi-truck"
        },
        {
            "title": "Returns & Refunds",
            "description": "Learn about our return policy",
            "link": "/returns/",
            "icon": "bi-arrow-counterclockwise"
        },
    ]

    # Popular FAQs (example)
    faqs = ReturnFAQ.objects.all()[:5]  # adjust as needed

    # Popular help topics (dummy example)
    help_topics = [
        {
            "title": "Ordering",
            "icon": "bi-bag",
            "link": "/help-center/ordering/",
            "items": ["How to place an order", "Payment methods", "Order confirmation"]
        },
        {
            "title": "Shipping",
            "icon": "bi-truck",
            "link": "/help-center/shipping/",
            "items": ["Shipping options", "Delivery times", "Tracking orders"]
        },
        {
            "title": "Returns",
            "icon": "bi-arrow-counterclockwise",
            "link": "/help-center/returns/",
            "items": ["Return policy", "How to return", "Refund process"]
        },
    ]

    context = {
        "quick_actions": quick_actions,
        "self_help_resources": self_help_resources,
        "faqs": faqs,
        "help_topics": help_topics,
    }
    return render(request, "myapp/support.html", context)

# Live chat message endpoint
@csrf_exempt
def send_chat_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message")
        name = data.get("name", "Guest")
        email = data.get("email", "no-email@example.com")

        # Send email to support
        send_mail(
            subject=f"Live Chat from {name}",
            message=f"Name: {name}\nEmail: {email}\nMessage: {message}",
            from_email="noreply@yourdomain.com",
            recipient_list=["alicha3033@gamil.com"],
        )

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "error"}, status=400)
# myapp/views.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from .models import SupportMessage

# Only superusers can access admin chat dashboard
def admin_check(user):
    return user.is_superuser

@login_required
@user_passes_test(admin_check)
def chat_dashboard(request):
    messages = SupportMessage.objects.all().order_by('-created_at')
    context = {'messages': messages}
    return render(request, 'myapp/chat_dashboard.html', context)

@login_required
@user_passes_test(admin_check)
def reply_chat_message(request, message_id):
    message = get_object_or_404(SupportMessage, id=message_id)
    if request.method == "POST":
        reply_text = request.POST.get('reply')
        message.reply = reply_text
        message.is_answered = True
        message.save()
        # Optionally, send an email to the user with the reply
        send_mail(
            subject="Reply from Support Team",
            message=reply_text,
            from_email="support@yourdomain.com",
            recipient_list=[message.email],
        )
        return redirect('myapp:chat_dashboard')
    return render(request, 'myapp/reply_chat.html', {'message': message})
# myapp/views.py
from django.views.decorators.http import require_GET

@require_GET
def get_chat_messages(request):
    email = request.GET.get("email")
    if not email:
        return JsonResponse({"messages": []})
    
    messages = SupportMessage.objects.filter(email=email).order_by("created_at")
    response = []
    for msg in messages:
        response.append({
            "id": msg.id,
            "name": msg.name,
            "message": msg.message,
            "reply": msg.reply,
            "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
        msg.read_by_user = True
        msg.save()
    return JsonResponse({"messages": response})

def starter_page(request):
    return render(request, 'starter-page.html')

def shipping_information(request):
    delivery_options = [
        {
            'icon': 'bi-lightning-charge',
            'title': 'Express Delivery',
            'description': 'Delivery within 1-2 business days.',
            'time': '1-2 Business Days',
        },
        {
            'icon': 'bi-box-seam',
            'title': 'Standard Shipping',
            'description': 'Delivery within 3-5 business days.',
            'time': '3-5 Business Days',
        },
        {
            'icon': 'bi-pin-map',
            'title': 'Local Shipping',
            'description': 'Delivery within 2-3 business days.',
            'time': '2-3 Business Days',
        },
    ]

    shipping_rates = [
        {'type': 'Standard Shipping', 'cost': 'ksh5.99', 'info': 'For orders under ksh50'},
        {'type': 'Free Shipping', 'cost': 'ksh0.00', 'info': 'For orders over ksh50', 'highlight': True},
        {'type': 'Express Shipping', 'cost': 'ksh12.99', 'info': '1-2 business days delivery'},
    ]

    international_shipping = [
        {'icon': 'bi-clock-history', 'title': 'Delivery Time', 'text': '5-10 business days for most international destinations'},
        {'icon': 'bi-currency-dollar', 'title': 'Customs & Duties', 'text': 'Import duties and taxes are not included in the shipping cost'},
        {'icon': 'bi-shield-check', 'title': 'Reliable Service', 'text': 'Tracked shipping with leading international carriers'},
    ]

    faqs = [
        {
            'question': "How can I track my order?",
            'answer': "You can track your order using the tracking number provided in your shipping confirmation email.",
        },
        {
            'question': "What if I'm not home for delivery?",
            'answer': "The carrier will leave a notification and attempt delivery again or leave your package at a secure location.",
        },
        {
            'question': "Do you offer weekend delivery?",
            'answer': "Weekend delivery is available for express shipping in select areas.",
        },
    ]

    return render(request, 'shipping-information.html', {
        'delivery_options': delivery_options,
        'shipping_rates': shipping_rates,
        'international_shipping': international_shipping,
        'faqs': faqs,
    })

def send_order_confirmation_email(order):
    subject = f"Order Confirmation - Order #{order.id}"
    html_message = render_to_string('emails/order_confirmation.html', {'order': order})
    plain_message = strip_tags(html_message)
    from_email = 'your-email@example.com'
    to = order.customer.email

    send_mail(subject, plain_message, from_email, [to], html_message=html_message)

def search_results(request):
    return render(request, 'search-results.html')

def admin_required(user):
    return user.is_authenticated and user.is_staff

def product_details(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "product_details.html", {"product": product})
@user_passes_test(admin_required)
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            return redirect('myapp:category_products', category_id=product.category.id)
        else:
            # Load a default category if form is invalid
            category = form.cleaned_data.get('category') or Category.objects.first()
            products = Product.objects.filter(category=category)
            return render(request, 'category.html', {
                'add_product_form': form,
                'products': products,
                'category': category
            })
    return redirect('/')

@user_passes_test(admin_required)
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.description = request.POST.get('description')

        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        product.save()
        return redirect('myapp:product_details')
    return redirect('/')

@user_passes_test(admin_required)

@login_required
@user_passes_test(is_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == "POST":
        # Use the correct attribute 'title' instead of 'name'
        product_title = product.title  
        product.delete()
        messages.success(request, f'Product "{product_title}" has been deleted.')
        return redirect("myapp:product_list")
    
    # Optional: redirect if GET request
    return redirect("myapp:product_list")
@login_required
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code')
        # TODO: Add coupon validation logic here
        # For now, just redirect to cart page
        return redirect('myapp:cart')
    else:
        return redirect('myapp:cart')

def calculate_cart_totals(cart_items):
    total_quantity = sum(item.quantity for item in cart_items)
    total_price = sum(item.quantity * item.product.price for item in cart_items)
    return {
        'total_quantity': total_quantity,
        'total_price': total_price,
    }
from django.utils import timezone
from datetime import timedelta
from .models import Product

def flash_sale(request):
    products = Product.objects.filter(is_flash_sale=True)
    return render(request, 'myapp/product_list.html', {'products': products, 'title': 'Flash Sale'})

def new_arrivals(request):
    last_30_days = timezone.now() - timedelta(days=30)
    products = Product.objects.filter(created_at__gte=last_30_days)
    return render(request, 'myapp/product_list.html', {'products': products, 'title': 'New Arrivals'})

def best_sellers(request):
    products = Product.objects.filter(is_best_seller=True)
    return render(request, 'myapp/product_list.html', {'products': products, 'title': 'Best Sellers'})

