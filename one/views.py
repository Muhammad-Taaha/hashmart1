from django.shortcuts import render
from django.db.models import Avg
from .models import One, Rating
from .forms import U_form,User_registration
from django.shortcuts import get_object_or_404 ,redirect
from django.shortcuts import render, get_object_or_404, redirect
from .models import One
from .models import Cart,Cartitems
from .forms import U_form
from .forms import RatingForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from huggingface_hub import InferenceClient
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponse
import requests
import traceback
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render
import datetime
import hmac
import hashlib
from django.views.decorators.csrf import csrf_exempt


# Home Page View
def index(request):
    return render(request, 'index.html')

def all_list(request):
    posts = One.objects.all().order_by("-created_at")
    print("DEBUG - Posts:", list(posts.values('id', 'text')))  # Print actual data
    context = {
        'posts': posts,
        'debug_test': "THIS SHOULD APPEAR IN TEMPLATE"
    }
    return render(request, "all_list.html", context)
# Create New Item View
@login_required
def create(request):
    if request.method == "POST":
        form = U_form(request.POST, request.FILES)
        if form.is_valid():
            one = form.save(commit=False)
            one.user = request.user  
            one.save()
            return redirect("one:all_list")  
    else:
        form = U_form()
    return render(request, "Oneform.html", {'form': form})

def edit(request, post_id):
    post = get_object_or_404(One, pk=post_id, user=request.user)
    if request.method == "POST":
        form = U_form(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()  # Save the post with the updated information
            return redirect("one:all_list")
    else:
        form = U_form(instance=post)
    return render(request, "Oneform.html", {'form': form})


# Delete an Item View
@login_required
def delete(request, post_id):
    post = get_object_or_404(One, pk=post_id, user=request.user)
    if request.method == "POST":
        post.delete()
        return redirect("one:all_list")
    return render(request, "delete.html", {'post': post})

def register(request):
    if request.method == "POST":
        form = User_registration(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            return redirect("one:all_list")
    else:
        form = User_registration()
    return render(request, "registration/register.html", {'form': form})



hf_token = "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"
repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
client = InferenceClient(model=repo_id, token=hf_token)



def chat_view(request):
    user_message = ''
    bot_response = ''

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()

        if user_message:
            # Send the message to the Hugging Face API
            headers = {
                "Authorization": f"Bearer {hf_token}"
            }
            data = {
                "inputs": user_message
            }

            url = f"https://api-inference.huggingface.co/models/{repo_id}"

            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                bot_response = response.json()[0]['generated_text']
            else:
                bot_response = f"Error: {response.status_code}, {response.text}"
        else:
            bot_response = "Please say something!"

    return render(request, 'chat.html', {
        'user_message': user_message,
        'bot_response': bot_response
    })


def empty_chat_view(request):
    return render(request, 'chat.html')
from django.contrib.auth.models import User

# User's Posts View
def user_posts(request, username):
    user = get_object_or_404(User, username=username)
    posts = One.objects.filter(user=user)
    return render(request, 'user_posts.html', {'user': user, 'posts': posts})

def create(request):
    if request.method == "POST":
        form = U_form(request.POST, request.FILES)
        if form.is_valid():
            one = form.save(commit=False)
            one.user = request.user
            one.save()
            return redirect("one:all_list")  # Redirect to the all_list page after saving the post
    else:
        form = U_form()
    return render(request, "Oneform.html", {'form': form})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Avg
from .models import One, Rating
from django.contrib.auth.models import User

def user_posts(request, username):
    user = get_object_or_404(User, username=username)
    posts = One.objects.filter(user=user)

    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        rating_input = request.POST.get('rating', '')

        try:
            rating_value = float(rating_input)
        except ValueError:
            messages.error(request, "Invalid rating value.")
            return redirect('one:user_posts', username=username)

        post = get_object_or_404(One, id=post_id)

        # Prevent self-rating
        if request.user == post.user:
            messages.error(request, "You can't rate your own post.")
        else:
            # Check if the user has already rated the post
            existing_rating = Rating.objects.filter(user=request.user, post=post).first()

            if existing_rating:
                messages.error(request, "You have already rated this post.")
            else:
                # Create a new rating record
                Rating.objects.create(post=post, user=request.user, value=rating_value)

                # Calculate the new average rating for the post
                ratings = Rating.objects.filter(post=post)
                avg_rating = ratings.aggregate(Avg('value'))['value__avg']

                # Update the post rating
                post.rating = round(avg_rating, 2) if avg_rating is not None else 0
                post.save()

                messages.success(request, "Your rating has been added.")

    return render(request, 'user_posts.html', {'user': user, 'posts': posts})

@login_required
def post_detail(request, post_id):
    post = One.objects.get(id=post_id)

    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        if rating_value:
            rating_value = float(rating_value)

            # Check if the user has already rated this post
            existing_rating = Rating.objects.filter(post=post, user=request.user).first()

            if existing_rating:
                existing_rating.value = rating_value  # Update existing rating
                existing_rating.save()
            else:
                Rating.objects.create(post=post, user=request.user, value=rating_value)  # Create new rating

            # Update the average rating for the post
            post.update_average_rating()

            return redirect('one:post_detail', post_id=post.id)  # Reload the page with the updated rating

    return render(request, 'post_detail.html', {'post': post})

@csrf_exempt
@login_required
def addtocart(request, post_id, username):
    # Get the post and user or return a 404 if not found
    post = get_object_or_404(One, id=post_id)
    user = get_object_or_404(User, username=username)

    # Handle the POST request (when adding an item to the cart)
    if request.method == "POST":
        try:
            quantity = int(request.POST.get('quantity', '1'))  # Default quantity is 1
            if quantity < 1:
                quantity = 1
        except ValueError:
            quantity = 1

        # Check if quantity exceeds available stock
        if quantity > post.quantity:
            messages.error(request, f"Only {post.quantity} items are available in stock!")
            return redirect('one:all_list')

        product_price = post.price

        # Get or create the cart for the user (assuming is_paid=False for an active cart)
        cart, created = Cart.objects.get_or_create(user=user, is_paid=False)

        # Get or create the cart item for the product
        cartitem, created_item = Cartitems.objects.get_or_create(cart=cart, product=post)

        # Update the quantity of the item in the cart
        if created_item:
            cartitem.quantity = quantity
        else:
            cartitem.quantity += quantity

        # Update the total price of the cart item
        cartitem.price = product_price * cartitem.quantity
        cartitem.save()

        # Get all cart items to display in the cart view
        cart_items = cart.cartitems.all()
        total_price = sum(item.price for item in cart_items)  
        # Render the cart page with updated items
        return render(request, 'addtocart.html', {
            'cart': cart,
            'post': post,
            'cart_items': cart_items,
            'username': user.username,
            'total_price':total_price
        })
    
    # Handle the GET request (show the cart page)
    else:
        # You can display an empty cart or a cart preview here
        cart, created = Cart.objects.get_or_create(user=user, is_paid=False)
        cart_items = cart.cartitems.all()  # Get the user's cart items

        return render(request, 'addtocart.html', {
            'cart': cart,
            'cart_items': cart_items,
            'username': user.username,
           
        })




import hmac, hashlib
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404
from .models import One  # replace with your actual model

JAZZCASH_MERCHANT_ID = "MC150925"
JAZZCASH_PASSWORD = "u39a1z3823"
JAZZCASH_RETURN_URL = "http://127.0.0.1:8000/one/payment-response/"
JAZZCASH_INTEGRITY_SALT = "z3duy108ff"
@csrf_exempt
def generate_secure_hash(data, integrity_salt):
    sorted_keys = sorted(data.keys())
    hash_string = integrity_salt + '&' + '&'.join(str(data[k]) for k in sorted_keys)
    return hmac.new(
        integrity_salt.encode('utf-8'),
        hash_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest().upper()

def checkin(request, post_id):
    post = get_object_or_404(One, id=post_id)
    product_name = post.text
    product_price = post.price

    pp_Amount = str(int(product_price * 100))  # Convert to paisa
    current_datetime = datetime.now()
    pp_TxnDateTime = current_datetime.strftime('%Y%m%d%H%M%S')
    pp_TxnExpiryDateTime = (current_datetime + timedelta(hours=1)).strftime('%Y%m%d%H%M%S')
    pp_TxnRefNo = "T" + pp_TxnDateTime

    post_data = {
        "pp_Version": "1.1",
        "pp_TxnType": "MWALLET",
        "pp_Language": "EN",
        "pp_MerchantID": JAZZCASH_MERCHANT_ID,
        "pp_Password": JAZZCASH_PASSWORD,
        "pp_TxnRefNo": pp_TxnRefNo,
        "pp_Amount": pp_Amount,
        "pp_TxnCurrency": "PKR",
        "pp_TxnDateTime": pp_TxnDateTime,
        "pp_BillReference": "billRef",
        "pp_Description": product_name,
        "pp_TxnExpiryDateTime": pp_TxnExpiryDateTime,
        "pp_ReturnURL": JAZZCASH_RETURN_URL,
        "pp_MobileNumber": "03001234567",  # Add this if needed
    }

    # Generate SecureHash
    post_data["pp_SecureHash"] = generate_secure_hash(post_data, JAZZCASH_INTEGRITY_SALT)

    return render(request, 'one/success.html', {
        'product_name': product_name,
        'product_price': product_price,
        'post_data': post_data
    })
@csrf_exempt
def checkout(request):
    user = request.user
    cart = get_object_or_404(Cart, user=user, is_paid=False)
    cart_items = cart.cartitems.all()
    total_price = sum(item.price for item in cart_items)
    product_name = f"{user.username}'s Cart"
    pp_Amount = str(int(total_price * 100))
    current_datetime = datetime.now()
    pp_TxnDateTime = current_datetime.strftime('%Y%m%d%H%M%S')
    pp_TxnExpiryDateTime = (current_datetime + timedelta(hours=1)).strftime('%Y%m%d%H%M%S')
    pp_TxnRefNo = "T" + pp_TxnDateTime

    # JazzCash required data
    post_data = {
        "pp_Version": "1.1",
        "pp_TxnType": "MWALLET",
        "pp_Language": "EN",
        "pp_MerchantID": JAZZCASH_MERCHANT_ID,
        "pp_Password": JAZZCASH_PASSWORD,
        "pp_TxnRefNo": pp_TxnRefNo,
        "pp_Amount": pp_Amount,
        "pp_TxnCurrency": "PKR",
        "pp_TxnDateTime": pp_TxnDateTime,
        "pp_BillReference": "CartPayment",
        "pp_Description": product_name,
        "pp_TxnExpiryDateTime": pp_TxnExpiryDateTime,
        "pp_ReturnURL": JAZZCASH_RETURN_URL,
    }

    # Secure hash
    sorted_string = '&'.join(f"{key}={value}" for key, value in sorted(post_data.items()))
    pp_SecureHash = hmac.new(
        JAZZCASH_INTEGRITY_SALT.encode('utf-8'),
        sorted_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest().upper()

    post_data["pp_SecureHash"] = pp_SecureHash

    return render(request, 'checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price,
        'product_name': product_name,
        'post_data': post_data,
    })



def drop_cart(request, post_id, username):
   
    post = get_object_or_404(One, id=post_id)
    user = get_object_or_404(User, username=username)
    cart = Cart.objects.get_or_create(user=user, is_paid=False)[0]
    cartitem = Cartitems.objects.filter(cart=cart, product=post).first()
    
    if cartitem:
        cartitem.delete()  
        messages.success(request, f"{post.text} has been removed from your cart.")
    else:
        messages.error(request, f"{post.text} is not in your cart.")

    
    return redirect('one:addtocart', post_id=post.id, username=user.username)



def view_cart(request, username):
    user = get_object_or_404(User, username=username)
    cart, created = Cart.objects.get_or_create(user=user, is_paid=False)
    cart_items = cart.cartitems.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'addtocart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price,
        'username': username
    })
from django.shortcuts import render
@csrf_exempt
def generate_jazzcash_hash(txn_ref, amount, bill_reference, description, return_url, secret_key):
    # Combine the string for hashing
    hash_string = f"{txn_ref}|{amount}|{bill_reference}|{description}|{return_url}|{secret_key}"
    
    # Generate the MD5 hash
    hash_value = hashlib.md5(hash_string.encode('utf-8')).hexdigest()
    
    return hash_value


from datetime import datetime, timedelta

# def jazzcash_payment(request):
#     if request.method == 'POST':
#         merchant_id = 'MC150925'
#         password = 'u39a1z3823'
#         integrity_salt = 'z3duy108ff'
#         txn_ref = 'T' + datetime.now().strftime('%Y%m%d%H%M%S')  # Generates dynamic ref
#         txn_datetime = datetime.now().strftime('%Y%m%d%H%M%S')
#         txn_expiry = (datetime.now() + timedelta(hours=1)).strftime('%Y%m%d%H%M%S')

#         data = {
#             'pp_Version': '1.1',
#             'pp_TxnType': 'MWALLET',
#             'pp_Language': 'EN',
#             'pp_MerchantID': merchant_id,
#             'pp_Password': password,
#             'pp_TxnRefNo': txn_ref,
#             'pp_Amount': '1000',  # Amount in paisa (e.g., 1000 = Rs. 10.00)
#             'pp_TxnCurrency': 'PKR',
#             'pp_TxnDateTime': txn_datetime,
#             'pp_BillReference': 'billRef',
#             'pp_Description': 'Description of transaction',
#             'pp_TxnExpiryDateTime': txn_expiry,
#             'pp_ReturnURL': 'http://127.0.0.1:8000/one/all/',
#             'pp_SecureHash': '',  # Placeholder, to be generated
#             'ppmpf_1': '',
#             'ppmpf_2': '',
#             'ppmpf_3': '',
#             'ppmpf_4': '',
#             'ppmpf_5': '',
#         }
#         print(data)
#         # Create Secure Hash String
#         hash_string = integrity_salt + '&' + '&'.join(
#             str(v) for k, v in sorted(data.items()) if v and k != 'pp_SecureHash'
#         )

#         # Generate HMAC SHA256 hash
#         secure_hash = hmac.new(
#             integrity_salt.encode('utf-8'),
#             hash_string.encode('utf-8'),
#             hashlib.sha256
#         ).hexdigest()

#         data['pp_SecureHash'] = secure_hash
#         print(data)
#         return render(request, 'jazzcash_payment.html', {
#             **data,
#             'salt': integrity_salt,
#             'hashValuesString': hash_string,
#         })
#     else:
#         return render(request, 'jazzcash_payment.html')
# 

import hmac
import hashlib
from datetime import datetime, timedelta
from django.shortcuts import render
@csrf_exempt
def jazzcash_payment(request):
    if request.method == 'POST':
        merchant_id = 'MC150925'
        password = 'u39a1z3823'
        integrity_salt = 'z3duy108ff'

        txn_ref = 'T' + datetime.now().strftime('%Y%m%d%H%M%S')
        txn_datetime = datetime.now().strftime('%Y%m%d%H%M%S')
        txn_expiry = (datetime.now() + timedelta(hours=1)).strftime('%Y%m%d%H%M%S')

        data = {
            'pp_Version': '1.1',
            'pp_TxnType': 'MWALLET',
            'pp_Language': 'EN',
            'pp_MerchantID': merchant_id,
            'pp_Password': password,
            'pp_TxnRefNo': 'T20250416185333',
            'pp_Amount': '10000',  # amount in paisa
            'pp_TxnCurrency': 'PKR',
            'pp_TxnDateTime': txn_datetime,
            'pp_BillReference': 'billRef123',
            'pp_Description': 'Payment for product XYZ',
            'pp_TxnExpiryDateTime': txn_expiry,
            'pp_ReturnURL': 'http://127.0.0.1:8000/one/all/',
            'ppmpf_1': '',
            'ppmpf_2': '',
            'ppmpf_3': '',
            'ppmpf_4': '',
            'ppmpf_5': '',
        }

        # Step 1: Build the string to hash
        hash_string = integrity_salt + '&' + '&'.join(
            str(v) for k, v in sorted(data.items()) if k != 'pp_SecureHash' and v
        )

        # Step 2: Generate HMAC SHA256 hash
        secure_hash = hmac.new(
            integrity_salt.encode('utf-8'),
            hash_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().upper()

        # Step 3: Add SecureHash and remove sensitive info
        data['pp_SecureHash'] = '4BEA768026193753FC4EA1B0C67354C4A3FE78C9A2111C34368E29C093B90EBD'
        del data['pp_Password']

        return render(request, 'jazzcash_payment.html', {'data': data})

    else:
        return render(request, 'jazzcash_payment.html', {'data': {}})


def search_view(request):
    username_query = request.GET.get('username')
    searched_user = None
    posts = []
    searched = False

    if username_query:
        searched = True
        try:
            searched_user = User.objects.get(username=username_query)
            posts = One.objects.filter(user=searched_user)
        except User.DoesNotExist:
            searched_user = None

    context = {
        'searched_user': searched_user,
        'posts': posts,
        'searched': searched,
    }

    return render(request, 'search.html', context)
def about(request):
    return render(request,'about.html')
from django.shortcuts import render
from django.db.models import Sum
from django.contrib.auth.models import User
from one.models import Cart, Cartitems, Rating

def dashboard_view(request):
    # Total registered users
    total_users = User.objects.count()

    # Sum of all orders' total price
    total_revenue = Cart.objects.aggregate(Sum('cartitems__price'))['cartitems__price__sum'] or 0

    # Total number of orders (carts)
    total_orders = Cart.objects.count()

    # Top 5 selling products based on quantity sold
    top_products = Cartitems.objects.values('product__text').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]
    avg_ratings = One.objects.annotate(average_rating=Avg('ratings__value')).order_by('-average_rating')[:5]
    # Pass the analytics data to template
    context = {
        'total_users': total_users,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'top_products': list(top_products),  # Convert QuerySet to list
    }

    return render(request, 'dashboard.html', context)
