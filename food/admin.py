from django.contrib import admin

# Register your models here.

from .models import Category, Customer, Order, OrderItem, Product, ProductVariation


admin.site.site_header = "Food Factory"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Food Factory Mangement Portal"


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'address')  # Columns to display in the list view
    search_fields = ('name', 'phone', 'email')  # Searchable fields
    list_filter = ('name',)  # Filters for the list view


# Category Admin
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')  # Columns to display
    search_fields = ('name',)  # Searchable field


# Product Admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_available')  # Display product name, category, availability
    search_fields = ('name', 'category__name')  # Searchable by name and category
    list_filter = ('category', 'is_available')  # Filters by category and availability


# Product Variation Admin
class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'price')  # Display product name, size, and price
    search_fields = ('product__name', 'size')  # Searchable by product name and size
    list_filter = ('size',)  # Filters by size


# Order Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order_date', 'status', 'order_type')  # Display order details
    search_fields = ('customer__name', 'status', 'order_type')  # Searchable by customer, status, and order type
    list_filter = ('status', 'order_type')  # Filters by status and order type
    date_hierarchy = 'order_date'  # Add a date hierarchy for orders


# Order Item Admin
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_variation', 'quantity')  # Display order, product variation, and quantity
    search_fields = ('order__id', 'product_variation__product__name')  # Searchable by order ID and product name
    list_filter = ('product_variation__size',)  # Filter by product size


# Register the models with the admin site
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Category, CategoryAdmin)
# admin.site.register(Product, ProductAdmin)
# admin.site.register(ProductVariation, ProductVariationAdmin)
# admin.site.register(Order, OrderAdmin)
# admin.site.register(OrderItem, OrderItemAdmin)