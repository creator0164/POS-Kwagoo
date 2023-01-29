from pickle import FALSE
from django.shortcuts import redirect, render
from django.http import HttpResponse
from posApp.models import Category, Products, Sales, salesItems
from django.db.models import Count, Sum
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import json
import sys
from datetime import date, datetime
# get all users
from django.contrib.auth.models import User

# Login


def login_user(request):
    logout(request)
    resp = {"status": 'failed', 'msg': ''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status'] = 'success'
            elif user.is_active:
                resp['msg'] = "You are not allowed to login here You are not an normal user"
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp), content_type='application/json')

# Logout


def logoutuser(request):
    logout(request)
    return redirect('/')

# Create your views here.


@login_required
def home(request):
    if request.user.is_active and not request.user.is_staff and not request.user.is_superuser:
        return redirect('pos-page')
    now = datetime.now()
    current_year = now.strftime("%Y")
    current_month = now.strftime("%m")
    current_day = now.strftime("%d")
    categories = len(Category.objects.all())
    products = len(Products.objects.all())
    transaction = len(Sales.objects.filter(
        user_sales=request.user,
        date_added__year=current_year,
        date_added__month=current_month,
        date_added__day=current_day
    ))
    today_sales = Sales.objects.filter(
        user_sales=request.user,
        date_added__year=current_year,
        date_added__month=current_month,
        date_added__day=current_day
    ).all()
    total_sales = sum(today_sales.values_list('grand_total', flat=True))
    context = {
        'page_title': 'Home',
        'categories': categories,
        'products': products,
        'transaction': transaction,
        'total_sales': total_sales,
    }
    return render(request, 'posApp/home.html', context)


def about(request):
    context = {
        'page_title': 'About',
    }
    return render(request, 'posApp/about.html', context)

# Categories


@login_required
def category(request):
    category_list = Category.objects.all()
    # category_list = {}
    context = {
        'page_title': 'Category List',
        'category': category_list,
    }
    return render(request, 'posApp/category.html', context)


@login_required
def manage_category(request):
    category = {}
    if request.method == 'GET':
        data = request.GET
        id = ''
        if 'id' in data:
            id = data['id']
        if id.isnumeric() and int(id) > 0:
            category = Category.objects.filter(id=id).first()

    context = {
        'category': category
    }
    return render(request, 'posApp/manage_category.html', context)


@login_required
def save_category(request):
    data = request.POST
    resp = {'status': 'failed'}
    try:
        if (data['id']).isnumeric() and int(data['id']) > 0:
            save_category = Category.objects.filter(id=data['id']).update(
                name=data['name'], description=data['description'], status=data['status'])
        else:
            save_category = Category(
                name=data['name'], description=data['description'], status=data['status'])
            save_category.save()
        resp['status'] = 'success'
        messages.success(request, 'Category Successfully saved.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def delete_category(request):
    data = request.POST
    resp = {'status': ''}
    try:
        Category.objects.filter(id=data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Category Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

# Products


@login_required
def products(request):
    product_list = Products.objects.all()
    context = {
        'page_title': 'Product List',
        'products': product_list,
    }
    return render(request, 'posApp/products.html', context)


@login_required
def manage_products(request):
    product = {}
    categories = Category.objects.filter(status=1).all()
    if request.method == 'GET':
        data = request.GET
        id = ''
        if 'id' in data:
            id = data['id']
        if id.isnumeric() and int(id) > 0:
            product = Products.objects.filter(id=id).first()

    context = {
        'product': product,
        'categories': categories
    }
    return render(request, 'posApp/manage_product.html', context)


@login_required
def manage_users(request):
    user = {}
    if request.method == 'GET':
        data = request.GET
        id = ''
        if 'id' in data:
            id = data['id']
        category = ''
        no = 'yes'
        if id.isnumeric() and int(id) > 0:
            user = User.objects.filter(id=id).first()
            if user.is_active and user.is_staff and user.is_superuser:
                category = 'Admin'
            elif user.is_active and user.is_staff:
                category = 'Employee'
            else:
                category = 'User'
            no = 'no'

    context = {
        'user': user,
        'category': category,
        'no': no
    }
    return render(request, 'posApp/manage_users.html', context)


def test(request):
    categories = Category.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'posApp/test.html', context)


@login_required
def save_product(request):
    data = request.POST
    resp = {'status': 'failed'}
    id = ''
    if 'id' in data:
        id = data['id']
    if id.isnumeric() and int(id) > 0:
        check = Products.objects.exclude(id=id).filter(code=data['code']).all()
    else:
        check = Products.objects.filter(code=data['code']).all()
    if len(check) > 0:
        resp['msg'] = "Product Code Already Exists in the database"
    else:
        category = Category.objects.filter(id=data['category_id']).first()
        try:
            if (data['id']).isnumeric() and int(data['id']) > 0:
                save_product = Products.objects.filter(id=data['id']).update(
                    code=data['code'], category_id=category, name=data['name'], description=data['description'], price=float(data['price']), status=data['status'])
                print('bs')
            else:
                save_product = Products(code=data['code'], category_id=category, name=data['name'],
                                        description=data['description'], price=float(data['price']), status=data['status'])
                save_product.save()
            resp['status'] = 'success'
            messages.success(request, 'Product Successfully saved.')
        except:
            resp['status'] = 'failed'

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def save_user(request):
    data = request.POST
    resp = {'status': 'failed'}
    id = ''
    if 'id' in data:
        id = data['id']
    print(id, 'dada', )
    if id.isnumeric() and User.objects.exclude(id=id).filter(username__iexact=data['username']).exists():
        print('aaa')
        resp['msg'] = 'Username is already Exist.'
    elif User.objects.exclude(id=id).filter(username__iexact=data['username']).exists():
        resp['msg'] = 'Username is already Exist.'
    else:
        try:
            if data['category_id'] == 'Admin':
                category = {'is_active': True,
                            'is_staff': True, 'is_superuser': True}
            elif data['category_id'] == 'Employee':
                category = {'is_active': True, 'is_staff': True}
            else:
                category = {'is_active': True, }

            if (data['id']).isnumeric() and int(data['id']) > 0:
                save_user = User.objects.filter(id=data['id']).update(
                    username=data['username'],
                    email=data['email'],
                    first_name=data['fname'],
                    last_name=data['lname'],
                    **category,
                )
            else:
                # save_product = User(code=data['code'], category_id=category, name=data['name'],
                #                         description=data['description'], price=float(data['price']), status=data['status'])
                save_user = User(username=data['username'], email=data['email'], first_name=data['fname'],
                                 last_name=data['lname'], **category,)
                save_user.set_password(data['password'])

                save_user.save()
            resp['status'] = 'success'
            messages.success(request, 'Product Successfully saved.')
        except:
            resp['status'] = 'failed'

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def delete_product(request):
    data = request.POST
    resp = {'status': ''}
    try:
        Products.objects.filter(id=data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Product Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_user(request):
    data = request.POST
    resp = {'status': ''}
    try:
        User.objects.filter(id=data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Product Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def pos(request):
    products = Products.objects.filter(status=1)
    product_json = []
    for product in products:
        product_json.append(
            {'id': product.id, 'name': product.name, 'price': float(product.price)})
    context = {
        'page_title': "Point of Sale",
        'products': products,
        'product_json': json.dumps(product_json)
    }
    # return HttpResponse('')
    return render(request, 'posApp/pos.html', context)


@login_required
def checkout_modal(request):
    grand_total = 0
    if 'grand_total' in request.GET:
        grand_total = request.GET['grand_total']
    context = {
        'grand_total': grand_total,
    }
    return render(request, 'posApp/checkout.html', context)


@login_required
def save_pos(request):
    resp = {'status': 'failed', 'msg': ''}
    data = request.POST
    pref = datetime.now().year + datetime.now().year
    i = 1
    while True:
        code = '{:0>5}'.format(i)
        i += int(1)
        check = Sales.objects.filter(code=str(pref) + str(code)).all()
        if len(check) <= 0:
            break
    code = str(pref) + str(code)

    try:

        sales = Sales(code=code, sub_total=data['sub_total'], tax=data['tax'], tax_amount=data['tax_amount'],
                      grand_total=data['grand_total'], tendered_amount=data['tendered_amount'], amount_change=data['amount_change'], user_sales=request.user, status=True if request.user.is_active and not request.user.is_staff and not request.user.is_superuser else False).save()
        sale_id = Sales.objects.last().pk
        i = 0
        for prod in data.getlist('product_id[]'):
            product_id = prod
            sale = Sales.objects.filter(id=sale_id).first()
            product = Products.objects.filter(id=product_id).first()
            qty = data.getlist('qty[]')[i]
            price = data.getlist('price[]')[i]
            total = float(qty) * float(price)
            print({'sale_id': sale, 'product_id': product,
                  'qty': qty, 'price': price, 'total': total})
            salesItems(sale_id=sale, product_id=product,
                       qty=qty, price=price, total=total).save()

            i += int(1)
        resp['status'] = 'success'
        resp['sale_id'] = sale_id
        messages.success(request, "Sale Record has been saved.")
    except:
        resp['msg'] = "An error occured"
        print("Unexpected error:", sys.exc_info()[0])
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def salesList(request):
    sales = Sales.objects.all()
    sale_data = []
    for sale in sales:
        data = {}
        for field in sale._meta.get_fields(include_parents=False):
            if field.related_model is None:
                data[field.name] = getattr(sale, field.name)
        data['items'] = salesItems.objects.filter(sale_id=sale).all()
        data['item_count'] = len(data['items'])
        data['user_sales'] = sale.user_sales
        if 'tax_amount' in data:
            data['tax_amount'] = format(float(data['tax_amount']), '.2f')
        # print(data)
        sale_data.append(data)
    # print(sale_data)
    context = {
        'page_title': 'Sales Transactions',
        'sale_data': sale_data,
    }
    # return HttpResponse('')
    return render(request, 'posApp/sales.html', context)


@login_required
def receipt(request):
    id = request.GET.get('id')
    sales = Sales.objects.filter(id=id).first()
    transaction = {}

    for field in Sales._meta.get_fields():
        if field.related_model is None:
            transaction[field.name] = getattr(sales, field.name)
    if 'tax_amount' in transaction:
        transaction['tax_amount'] = format(float(transaction['tax_amount']))
    ItemList = salesItems.objects.filter(sale_id=sales).all()
    context = {
        "transaction": transaction,
        "salesItems": ItemList
    }

    return render(request, 'posApp/receipt.html', context)
    # return HttpResponse('')


@login_required
def delete_sale(request):
    resp = {'status': 'failed', 'msg': ''}
    id = request.POST.get('id')
    try:
        delete = Sales.objects.filter(id=id).delete()
        resp['status'] = 'success'
        messages.success(request, 'Sale Record has been deleted.')
    except:
        resp['msg'] = "An error occured"
        print("Unexpected error:", sys.exc_info()[0])
    return HttpResponse(json.dumps(resp), content_type='application/json')


@login_required
def my_users(request):
    users = User.objects.all()
    context = {
        'users': users
    }
    return render(request, 'posApp/users.html', context)


@login_required
def transaction_code(request):
    return render(request, 'posApp/transaction_code.html')


@login_required
def reciept_code(request):
    try:

        code = request.GET.get('code')
        print('test')

        if not Sales.objects.filter(code=code).exists():
            # resp['status'] = 'blank'
            context = {
                'status': 'blank'
            }
            print('test1')
            return render(request, 'posApp/receipt_code.html', context)
        sales = Sales.objects.filter(code=code).first()
        
        transaction = {}
        for field in Sales._meta.get_fields():
            if field.related_model is None:
                transaction[field.name] = getattr(sales, field.name)
        if 'tax_amount' in transaction:
            transaction['tax_amount'] = format(
                float(transaction['tax_amount']))
        ItemList = salesItems.objects.filter(sale_id=sales).all()
        context = {
            "transaction": transaction,
            "salesItems": ItemList
        }
    except:
        print('a')
    return render(request, 'posApp/receipt_code.html', context)


def validation(request):
    try:
        resp = {}
        code = request.POST.get('code')
        print(code,'sassa')
        print(Sales.objects.filter(code=json.loads(code)).exists())
        if not Sales.objects.filter(code=json.loads(code)).exists():
            resp['status'] = 'not'
            print('test111')
        else:
            sales = Sales.objects.get(code=json.loads(code))
            if not sales.status:
                resp['status'] = 'failed'
                print(1)
    except Exception as e:
        print(e)
    return HttpResponse(json.dumps(resp), content_type="application/json")


def update_receipt(request):
    resp = {}
    try:

        code = request.POST.get('code')
        tendered = request.POST.get('tendered_amount')
        change = request.POST.get('change')

        if float(json.loads(change)) <= 0:
            resp = {'status': 'failed'}
        else:

            sale = Sales.objects.get(code=json.loads(code))
            sale.tendered_amount = tendered
            sale.amount_change = change
            sale.status = False
            sale.user_sales = request.user
            sale.save()
    except Exception as e:
        resp['error'] = e
        print(e)
    return HttpResponse(json.dumps(resp), content_type="application/json")


def register(request):
    if request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password1']
        password2 = request.POST['password2']

        # check if passwords match
        if password != password2:
            return redirect('register')  # redirect to register page

        # check if user already exists
        if User.objects.filter(username=username).exists():
            return redirect('register')  # redirect to register page

        # create new user
        user = User.objects.create_user(
            username=username,  password=password)
        user.save()
        return redirect('login')
    return render(request, 'posApp/register.html')


def register_validation(request):
    resp = {"status": 'failed', 'msg': ''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']



        user = User.objects.filter(username=username).exists()
        if user:
            resp['msg'] = 'Username already exists'
        elif password1 != password2:
            resp['msg'] = 'Passwords do not match'
        else:
            user = User.objects.create_user(
                username=username, password=password1)
            user.save()
            login(request, user)
            resp['status'] = 'success'
    return HttpResponse(json.dumps(resp), content_type='application/json')
