from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart_view'),
    path('api/remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('api/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('api/create-order/', views.create_order, name='create_order'),
    path('api/order-status/<str:order_id>/', views.order_status, name='order_status'),
    path('api/send-message/', views.send_message, name='send_message'),
    path('api/client-info/', views.client_info, name='client_info'),
    path('order/<str:order_id>/', views.order_detail, name='order_detail'),
]
