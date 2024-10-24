from django.db import models
from django.utils import timezone
import uuid, os

# utils functions

def get_image_filename(instance, filename):
    """
    Generate a unique filename for the uploaded image.
    """
    ext = filename.split('.')[-1]  # Get the file extension
    filename = f"{uuid.uuid4()}.{ext}"  # Use a UUID to generate a unique filename
    return os.path.join('product_image/', filename)







# Create your models here.

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField( blank=True, null=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_image_filename, blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

class ProductVariation(models.Model):


    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    size = models.CharField(max_length=100, )
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.size}"
    

class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('Delivery', 'Delivery'),
        ('Dine-in', 'Dine-in'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer')
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('inprogress', 'In Progress'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ], default='In Progress')
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, default='Delivery')  # New field

    def __str__(self):
        return f"Order {self.id} - {self.customer}"
    
    @property
    def total_price(self):
        """Calculates the total price of the order."""
        return sum(item.product_variation.price * item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,  related_name='items')
    product_variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product_variation} (Order {self.order.id})"
