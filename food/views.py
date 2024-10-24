import datetime
from decimal import Decimal
from django.shortcuts import render, redirect,get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Product, ProductVariation, Category, Customer, Order, OrderItem

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.db.models import Sum, Count,  F

from .decorators import group_required

# Create your views here.






def login_user(request):
    if request.user.is_authenticated:
        return redirect('orders')
    msg=None
    context = {"msg": msg}

    if request.method == 'POST':
        print('in login')
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password, '<--')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('orders')
        else:
            msg="username or password incorrect"
            print(msg)
            # return render(request, 'login.html', context)
            return redirect('login_user')
    return render(request, 'auth/login.html', context)


@login_required(login_url='login_user')
def logout_user(request):
    logout(request)
    return redirect('login_user')








def dashboard(request):
    # Aggregate daily sales and order counts
    sales_data = (
        Order.objects.filter(status='Delivered')
        .values('order_date__date')
        .annotate(
            total_sales=Sum(F('items__product_variation__price')),
            order_count=Count('id')
        )
        .order_by('order_date__date')
    )

    # Prepare data for the graph
    labels = [str(sale['order_date__date']) for sale in sales_data]
    daily_sales = [float(sale['total_sales'] or Decimal(0)) for sale in sales_data]
    daily_order_counts = [sale['order_count'] for sale in sales_data]

    # Aggregate overall sales and delivered order count
    total_sales = float(Order.objects.filter(status='Delivered').aggregate(
        total_sales=Sum(F('items__product_variation__price'))
    )['total_sales'] or Decimal(0))

    total_delivered_orders = Order.objects.filter(status='Delivered').count()

    context = {
        'labels': labels,
        'daily_sales': daily_sales,
        'daily_order_counts': daily_order_counts,
        'total_sales': total_sales,
        'total_delivered_orders': total_delivered_orders,
    }

    return render(request, 'dashboard.html', context)

@login_required(login_url='login_user')
def products(request):
    return render(request, 'products/products.html')


@login_required(login_url='login_user')
def fetch_products(request):
    products = Product.objects.all().values(
        'id', 'name', 'description', 'category__name', 'is_available'
    )

    products_list = list(products)

    return JsonResponse({'products': products_list}, safe=False)
    




@login_required(login_url='login_user')
def add_product(request):
    if request.method == 'POST':
        # Handle the product data from the form
        product_name = request.POST.get('product_name')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        is_available = request.POST.get('is_available') == 'on'
        image = request.FILES.get('image')  # Handle image upload

        # Create the Product object
        category = Category.objects.get(id=category_id)
        product = Product.objects.create(
            name=product_name,
            description=description,
            category=category,
            image=image,
            is_available=is_available
        )

        # Handle the product variations
        sizes = request.POST.getlist('size[]')
        prices = request.POST.getlist('price[]')

        for size, price in zip(sizes, prices):
            ProductVariation.objects.create(
                product=product,
                size=size,
                price=price
            )

        return redirect('products')  # Redirect to a product list page or success page

    # If GET request, show the form
    categories = Category.objects.all()
    return render(request, 'products/add_product.html', {'categories': categories})


@login_required(login_url='login_user')
def delete_product(requset, id):
    try:

        product = Product.objects.get(id=id)
        product.delete()

        return JsonResponse({'msg': "Part deleted successfully"}, status=200, safe=False)
    except Exception as e :
        print('erro: ', e)
        return JsonResponse({'msg': "something went wrong"},status=400 , safe=False)


@login_required(login_url='login_user')
def fetch_product_variations(request, id):
    try:
        product = Product.objects.get(id=id)
        variations = list(ProductVariation.objects.filter(product=product).values())

        print(variations)
        return JsonResponse({'variations': variations}, status=200, safe=False)
    except Exception as e :
        print('erro: ', e)
        return JsonResponse({'msg': "something went wrong"},status=400 , safe=False)



@login_required(login_url='login_user')
def edit_product(request, id):
    product_id = id
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    existing_variations = ProductVariation.objects.filter(product=product)

    if request.method == 'POST':
        # Update product details
        product.name = request.POST.get('product_name')
        product.description = request.POST.get('description')
        product.category_id = request.POST.get('category')
        product.is_available = 'is_available' in request.POST

        if request.FILES.get('image'):
            product.image = request.FILES['image']

        product.save()

        # Get the submitted variation IDs
        submitted_variation_ids = request.POST.getlist('variation_id[]')

        # Delete variations that were removed in the form
        for variation in existing_variations:
            if str(variation.id) not in submitted_variation_ids:
                variation.delete()

        # Update existing variations or add new ones
        sizes = request.POST.getlist('size[]')
        prices = request.POST.getlist('price[]')

        for i, variation_id in enumerate(submitted_variation_ids):
            if variation_id:
                # Update existing variation
                variation = ProductVariation.objects.get(id=variation_id)
                variation.size = sizes[i]
                variation.price = prices[i]
                variation.save()
            else:
                # Create new variation
                ProductVariation.objects.create(
                    product=product,
                    size=sizes[i],
                    price=prices[i]
                )

        return redirect('products')

    return render(request, 'products/edit_product.html', {
        'product': product,
        'categories': categories,
        'variations': existing_variations,
    })

#  orders section ///////////////////////////////////////////

@login_required(login_url='login_user')
def orders(request):
    orders = Order.objects.all()
    return render(request, 'orders/order.html')

@login_required(login_url='login_user')
def fetch_orders(request):
    # Fetch all orders with related items and customer information
    orders = Order.objects.prefetch_related('items__product_variation').select_related('customer').order_by('-id')

    # Create a list of orders with relevant information
    orders_list = [
        {
            'id': order.id,
            'customer_phone': order.customer.phone,
            'status': order.status,
            'order_type': order.order_type,
            'order_date': order.order_date.strftime('%b %d %Y %I:%M %p'),
            'total_price': int(order.total_price)  # Accessing the property directly
        }
        for order in orders
    ]

    return JsonResponse({'orders': orders_list}, safe=False)
    



@login_required(login_url='login_user')
def create_order(request):
    products = Product.objects.prefetch_related('variations').all()
    customers = Customer.objects.all()

    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        order_type = request.POST.get('order_type')
        customer = get_object_or_404(Customer, id=customer_id)

        # Create the order
        order = Order.objects.create(customer=customer, order_type=order_type)

        # Get items and variations from the form
        product_ids = request.POST.getlist('product[]')
        variation_ids = request.POST.getlist('variation[]')
        quantities = request.POST.getlist('quantity[]')

        # Create order items
        for product_id, variation_id, quantity in zip(product_ids, variation_ids, quantities):
            variation = get_object_or_404(ProductVariation, id=variation_id)
            OrderItem.objects.create(order=order, product_variation=variation, quantity=int(quantity))

        return redirect('orders')

    return render(request, 'orders/add_order.html', {'products': products, 'customers': customers})

@login_required(login_url='login_user')
def delete_order(requset, id):
    try:

        order = Order.objects.get(id=id)
        order.delete()

        return JsonResponse({'msg': "Order deleted successfully"}, status=200, safe=False)
    except Exception as e :
        print('erro: ', e)
        return JsonResponse({'msg': "something went wrong"},status=400 , safe=False)



@login_required(login_url='login_user')
def edit_order(request, id):
    order_id = id
    order = get_object_or_404(Order, id=order_id)
    products = Product.objects.all()
    customers = Customer.objects.all()
    order_items = order.items.all()  # Fetch related order items

    if request.method == 'POST':
        # Update order details
        order.customer_id = request.POST.get('customer')
        order.status = request.POST.get('status')
        order.save()

        # Delete all existing order items to reset them
        order.items.all().delete()

        # Get data from the form
        product_ids = request.POST.getlist('product[]')
        variation_ids = request.POST.getlist('variation[]')
        quantities = request.POST.getlist('quantity[]')

        # Create new order items
        for i in range(len(product_ids)):
            product_id = product_ids[i]
            variation_id = variation_ids[i]
            quantity = quantities[i]

            # Fetch the selected product and variation
            product = Product.objects.get(id=product_id)
            variation = ProductVariation.objects.get(id=variation_id)

            # Ensure the variation belongs to the selected product
            if variation.product == product:
                OrderItem.objects.create(
                    order=order,
                    product_variation=variation,
                    quantity=quantity
                )
            else:
                # Handle the case where the variation doesn't belong to the selected product
                # You might want to raise an error or skip this case
                raise ValueError("Variation doesn't belong to the selected product!")

  
    return render(request, 'orders/edit_order.html', {
        'order': order,
        'customers': customers,
        'products': products,
        'order_items': order_items,
    })


# @group_required('kitchen', 'in_progress_orders')
def in_progress_orders(request):
    # Fetch in-progress orders ordered by the time they were placed (oldest first)
    orders = Order.objects.filter(status='In Progress').order_by('order_date').prefetch_related('items__product_variation')

    print(orders)    

    return render(request, 'orders/inprogress_orders.html', {'orders': orders})

@login_required(login_url='login_user')
def in_progress_orders_data(request):
    orders = Order.objects.filter(status='In Progress').order_by('order_date')

    orders_list = [
        {
            'id': order.id,
            'customer_name': order.customer.name,
            'customer_phone': order.customer.phone,
            'order_type': order.order_type,
            'order_date': order.order_date.strftime('%b %d %Y %I:%M %p'),
            'items': [
                {
                    'product_name': item.product_variation.product.name,
                    'size': item.product_variation.size,
                    'quantity': item.quantity,
                }
                for item in order.items.all()
            ],
        }
        for order in orders
    ]

    return JsonResponse({'orders': orders_list})


#  Create Customer 

@login_required(login_url='login_user')
def create_customer(request):
    if request.method == 'POST':
        try:
            Customer.objects.create(
                name=request.POST.get('name', None),
                email=request.POST.get('email', None),
                phone=request.POST.get('phone', None),
                address=request.POST.get('address', None),
            )
        except Exception as e:
            print('error: ', e)
        finally:
            return redirect('orders')


    return render(request, 'customers/add_customer.html')