from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib import messages
from decimal import Decimal
from .models import *


# User Registration
def register(request):
    if request.method == 'POST' and 'Registration' in request.POST:
        data = request.POST
        user = User.objects.create_user(
            first_name=data['fname'],
            last_name=data['lname'],
            email=data['email'],
            username=data['username'],
            password=data['password']
        )
        user.save()
        return redirect('registration')

    # User login
    if request.method == 'POST' and 'Login' in request.POST:
        data = request.POST
        user = authenticate(
            username=data['username'],
            password=data['password']
        )
        if user is not None:
            login(request, user)
            return redirect('products')

    return render(request, 'shop/register.html')


# Login user
def loginpage(request):
    return render(request, '')


# Logout user
def logout_user(request):
    logout(request)
    return redirect('registration')


def homepage(request):
    search = search_product(request)

    products = Product.objects.filter(published=True).order_by('-created')[:8]

    context = {
        "products": products,
        'search': search
    }
    if search:
        return render(request, 'shop/searc_result.html', context)
    return render(request, 'shop/index.html', context)


def products(request):
    search = search_product(request)

    category = request.GET.get('category')
    if category == None:
        products = Product.objects.filter(published=True).order_by('-created')
    else:
        products = Product.objects.filter(
            published=True, category__category=category).order_by('-created')

    categories = Category.objects.all()[:15]
    # Pagination for product
    paginator = Paginator(products, 15)
    page_number = request.GET.get('page', 1)
    page_objects = paginator.get_page(page_number)

    context = {
        'products': products,
        'page_objects': page_objects,
        'categories': categories,
        'search': search
    }

    if search:
        return render(request, 'shop/searc_result.html', context)
    return render(request, 'shop/category.html', context)


def detail(request, pk):
    search = search_product(request)

    products = Product.objects.filter(published=True).order_by('-created')[:3]
    product = Product.objects.get(id=pk)

    context = {
        'product': product,
        'products': products,
        'search': search
    }
    if search:
        return render(request, 'shop/searc_result.html', context)
    return render(request, 'shop/detail.html', context)


@login_required(login_url='registration')
def cart(request):
    search = search_product(request)

    context = {
        'search': search
    }
    if search:
        return render(request, 'shop/searc_result.html', context)
    return render(request, 'shop/basket.html', context)


@login_required(login_url='registration')
def addtocart(request, pk):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=pk)
        order_item, created = OrderItem.objects.get_or_create(
            user=request.user,
            item=product,
            ordered=False
        )

        order_set = Order.objects.filter(user=request.user, ordered=False)
        if order_set.exists():
            order = order_set[0]
            # check if order item is in order
            if order.items.filter(item_id=product.id).exists():
                # update qunatity
                order_item.quantity += 1
                order_item.save()
            else:
                order.items.add(order_item)
                messages.info(request, 'Item added')
        else:
            order = Order.objects.create(user=request.user)
            order.items.add(order_item)

    return redirect('cart')


def removeCartItem(request, pk):
    product = get_object_or_404(Product, id=pk)
    order_set = Order.objects.filter(user=request.user, ordered=False)
    orderItems = OrderItem.objects.filter(user=request.user, item=product)
    if orderItems:
        orderItems.delete()

    return redirect('cart')


@login_required(login_url='registration')
def addWishList(request, pk):
    product = Product.objects.get(id=pk)
    wish_list = Wishlist(user=request.user, item=product)
    if not Wishlist.objects.filter(user=request.user, item=product).exists():
        wish_list.save()
    return redirect('detail', pk=pk)


@login_required(login_url='registration')
def viewWishList(request):
    search = search_product(request)

    items = Wishlist.objects.filter(user=request.user).order_by('-created')
    context = {
        'items': items,
        'search': search
    }
    if search:
        return render(request, 'shop/searc_result.html', context)
    return render(request, 'shop/customer-wishlist.html', context)


@login_required(login_url='registration')
def checkout(request):
    search = search_product(request)

    context = {
        'search': search
    }
    return render(request, 'shop/checkout1.html', context)


def delivery(request):
    search = search_product(request)

    context = {
        'search': search
    }
    if search:
        return render(request, 'shop/searc_result.html', context)
    return render(request, 'shop/checkout3.html', context)


def payment(request):
    search = search_product(request)

    context = {
        'search': search
    }
    if search:
        return render(request, 'shop/searc_result.html', context)
    return render(request, 'shop/checkout2.html', context)



def customer_account(request):
    search = search_product(request)
    if search:
        return render(request, 'shop/searc_result.html', {'search': search})
    if request.method == 'POST':
        data = request.POST
        user = User.objects.get(username=request.user)
        if data['password_1'] == data['password_2']:
            user.set_password(data['password_1'])
            user.save()
    return render(request, 'shop/customer-account.html')


def contact(request):
    search = search_product(request)

    context = {
        'search': search
    }
    if search:
        return render(request, 'shop/searc_result.html', context)
    return render(request, 'shop/contact.html', context)


def questions(request):
    search = search_product(request)
    context = {
        'search': search
    }
    if search:
        return render(request, 'shop/searc_result.html', context)
    return render(request, 'shop/faq.html')


# def search_resut(request):
#     return render(request, 'searc_result.html')


def search_product(request):
    if request.method == 'POST' and 'Search Product' in request.POST:
        data = request.POST
        quary = Product.objects.filter(
            published=True, name__contains=data['search'])
        print('Quary ==========', quary)
        return quary
