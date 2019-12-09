from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from shopping.forms import writereview
from .models import Category, Product, Review, DeliveryOptions
from .serializers import ProductSerializer, CategorySerializer
from user_auth.forms import DeliveryLocationForm, DeliveryLocation


def list_categories(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    form = DeliveryLocationForm()

    if DeliveryLocation.objects.filter(user_name=request.user).exists():
        delivery = DeliveryLocation.objects.get(user_name=request.user)
        form = DeliveryLocationForm(instance=delivery)
        if request.method == 'POST':
            form = DeliveryLocationForm(request.POST, instance=delivery)
            if form.is_valid():
                form.save()
                return redirect('shopping:home')
        return render(request, 'shopping/index.html',
                      {'categories': categories, 'products': products, 'Shopping': 'active', 'form': form,
                       'delivery_exists': True})

    if request.method == 'POST':
        form = DeliveryLocationForm(request.POST)
        if form.is_valid():
            u = User.objects.get(username=request.user.username)
            pin_code = form.cleaned_data['pin_code']
            DeliveryLocation.objects.create(user_name=u, pin_code=pin_code)
            return redirect('shopping:home')
        else:
            print('The form is not valid')
            print(form.errors)

    return render(request, 'shopping/index.html',
                  {'categories': categories, 'products': products, 'Shopping': 'active', 'form': form})


def itemsview(request, pk):
    categories = Category.objects.all()
    cat = Category.objects.get(id=pk)
    current_order_products = []
    # if request.user.is_authenticated:
    #     filtered_orders = Order.objects.filter(owner=request.user.cus, is_ordered=False)
    #     if filtered_orders.exists():
    #         user_order = filtered_orders[0]
    #         user_order_items = user_order.items.all()
    #         current_order_products = [product.product for product in user_order_items]

    context = {
        'categories': categories,
        'cat': cat,
        'current_order_products': current_order_products,
        'Shopping': 'active'
    }

    return render(request, "shopping/items.html", context)


def itemdetailview(request, pk, ck):
    categories = Category.objects.all()
    cat = Category.objects.get(id=pk)
    prod = Product.objects.get(id=ck)
    products = Product.objects.filter(category=cat)
    current_order_products = []

    if request.method == 'POST':
        form = writereview(request.POST)
        if form.is_valid():
            content = request.POST.get('content')
            rating = request.POST.get('rating')
            review1 = Review.objects.create(category=cat, product=prod, customer=request.user, content=content,
                                            rating=rating)
            review1.save()
            return redirect(reverse('shopping:specificitem', args=(pk, ck,)))
    else:
        form = writereview()
    return render(request, 'shopping/itemdetail.html', {'form': form,
                                                        'categories': categories,
                                                        'cat': cat,
                                                        'prod': prod,
                                                        'current_order_products': current_order_products,
                                                        'Shopping': 'active'})


@login_required
def reviewtext(request, categ, product):
    prod = get_object_or_404(Product, pk=product)
    cat = get_object_or_404(Category, pk=categ)
    if request.method == 'POST':
        form = writereview(request.POST)
        if form.is_valid():
            content = request.POST.get('content')
            rating = request.POST.get('rating')
            review1 = Review.objects.create(category=cat, product=prod, customer=request.user, content=content,
                                            rating=rating)
            review1.save()
            return redirect(reverse('shopping:specificitem', args=(product, categ,)))
    else:
        form = writereview()
    return render(request, 'shopping/writereview.html', {'form': form, 'Shopping': 'active'})


@api_view(['GET'])
def productList(request):
    if request.method == 'GET':
        products = Product.objects.all()
        for product in products:
            product.stock *= 0.1
        serializer = ProductSerializer(products, many=True)
        return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def categoriesList(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return JsonResponse(serializer.data, safe=False)


@api_view(['POST'])
def bidding(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        # t = Tournaments.objects.get(name=data['tournament'])
        # data['tournament'] = t.pk

        # tournament = get_object_or_404(Tournaments, title=request.data.get('tournament'))
        p_id = data['product']
        name = data['name']
        name_id = data['name_id']
        days = data['days']
        cost = data['cost']
        pincode = data['pincode']
        print(name,pincode)
        if data['msg'] == 'delete':
            try:
                product = Product.objects.get(pk=p_id)
                instance = DeliveryOptions.objects.get(product=product, name_id=name_id, pincode=pincode)
                instance.delete()
            except:
                return Response({'data is not valid'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'data deleted'}, status=status.HTTP_201_CREATED)

        else:
            try:
                product = Product.objects.get(pk=p_id)
                if DeliveryOptions.objects.filter(product=product, name_id=name_id, pincode=pincode).exists():
                    instance = DeliveryOptions.objects.get(product=product, name_id=name_id, pincode=pincode)
                    instance.cost = cost
                    instance.days = days
                    instance.name = name
                    instance.save()
                    return Response({'data update'}, status=status.HTTP_201_CREATED)
                else:
                    print('creating new row')
                    DeliveryOptions.objects.create(product=product, name=name, name_id=name_id, days=days, cost=cost, pincode=pincode)
                    return Response({'created'}, status=status.HTTP_201_CREATED)
            except:
                pass
            return Response({'Bad request'}, status=status.HTTP_400_BAD_REQUEST)
