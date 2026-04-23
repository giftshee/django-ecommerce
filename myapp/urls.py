from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    # --- Main Pages ---
    path('', views.home, name='index'),
    path('search/', views.search, name='search'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/remove-session/<int:item_id>/', views.remove_from_session_wishlist, name='remove_from_session_wishlist'),
    path('about/', views.about, name='about'),
    path('about/edit/<int:pk>/', views.edit_about, name='edit_about'),
    path('contact/', views.contact_page, name='contact'),
    path('account/', views.account, name='account'),
    path('starter-page/', views.starter_page, name='starter_page'),

    # --- Cart & Checkout ---
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_quantity, name='update_quantity'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),

    # --- Order Confirmation ---
    path('order-confirmation/', views.order_confirmation, name='order_confirmation_latest'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),

    # --- Payments & MPESA ---
    path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),

    # --- Products ---
    path('product/', views.product_list, name='product_list'),
    path('product/add/', views.product_add, name='product_add'),
    path('product/<int:pk>/', views.product_details, name='product_details'),
    path('product/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('product/delete/<int:pk>/', views.product_delete, name='product_delete'),

    # --- Categories ---
    path('category/', views.category, name='category'),  # All categories view
    path('category/<slug:slug>/', views.category, name='category_products'),  # Filter by slug

    path('brand/add/', views.add_brand, name='brand_add'),
    path('subcategory/add/<int:category_id>/', views.subcategory_add, name='subcategory_add'),
    path('subcategory/update/<int:pk>/', views.subcategory_update, name='subcategory_update'),
    path('subcategory/delete/<int:pk>/', views.subcategory_delete, name='subcategory_delete'),

    # --- Policies & Support ---
    path('privacy/', views.privacy, name='privacy'),
    path('return-policy/', views.return_policy, name='return_policy'),
    path('tos/', views.tos, name='tos'),
    path('payment-methods/', views.payment_methods, name='payment_methods'),
    path('support/', views.support_page, name='support'),
    path('send_chat_message/', views.send_chat_message, name='send_chat_message'),
    # myapp/urls.py
path('admin/chat-dashboard/', views.chat_dashboard, name='chat_dashboard'),
path('admin/chat-reply/<int:message_id>/', views.reply_chat_message, name='reply_chat_message'),
# myapp/urls.py
path('get_chat_messages/', views.get_chat_messages, name='get_chat_messages'),

    path('shipping-information/', views.shipping_information, name='shipping_information'),
    path('faq/', views.faq, name='faq'),

    # --- Search ---
    path('search-results/', views.search_results, name='search_results'),

    # --- Special Product Lists ---
    path('flash-sale/', views.flash_sale, name='flash_sale'),
    path('new-arrivals/', views.new_arrivals, name='new_arrivals'),
    path('best-sellers/', views.home, name='best_sellers'),
]
