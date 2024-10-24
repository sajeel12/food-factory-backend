

from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('',  views.products, name='products'),
    path('dashboard/',  views.dashboard, name='dashboard'),

    path('api/fetch-products/',  views.fetch_products,),
    path('add-product',  views.add_product, name='add_product'),
    path('api/delete-product/<int:id>/',  views.delete_product, name='add_product'),
    path('api/product-variations/<int:id>/',  views.fetch_product_variations, name='add_product'),
    path('edit-product/<int:id>/',  views.edit_product, name='edit_product'),


    path('orders',  views.orders, name='orders'),
    path('api/fetch-orders/',  views.fetch_orders),
    path('add-order',  views.create_order, name='add_order'),
    path('api/delete-order/<int:id>/',  views.delete_order),
    # path('api/delete-product/<int:id>/',  views.delete_product, name='add_product'),
    path('edit-order/<int:id>/',  views.edit_order, name='edit_order'),
    path('in-progress-orders/', views.in_progress_orders, name='in_progress_orders'),
    path('in-progress-orders-data/', views.in_progress_orders_data, name='in_progress_orders_data'),


    path('add-customer',  views.create_customer, name='add_customer'),

    path('login', views.login_user ,name='login_user'),
    path('logout', views.logout_user  ,name='logout_user')

]
