"""
URL configuration for hashmart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views
from .views import chat_view, empty_chat_view, addtocart,checkout,checkin,drop_cart,jazzcash_payment,search_view,about,dashboard_view
from django.contrib.auth import views as auth_views

app_name = 'one'  

urlpatterns = [
      
    path('', views.index, name="index"),  
    path('all/', views.all_list, name="all_list"), 
    path('create/', views.create, name="create"), 
    path('<int:post_id>/delete/', views.delete, name="delete"),  
    path('<int:post_id>/edit/', views.edit, name="edit"),  
    path('register/', views.register, name="register"),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('user/<str:username>/', views.user_posts, name='user_posts'),
    path('chat/', views.chat_view, name='chat'),
    path('empty-chat/', views.empty_chat_view, name='empty_chat_view'),
    path('addtocart/<int:post_id>/<str:username>/', views.addtocart, name='addtocart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkin/', checkin, name="checkin"),
    path('<int:post_id>/drop_cart/<str:username>/', views.drop_cart, name='drop_cart'),
    path('cart/<str:username>/', views.view_cart, name='view_cart'),
    path('jazzcash/', views.jazzcash_payment,name="jazzcash_payment"),
     path("search/", search_view, name="search_view"),
     path("about/", about, name="about"),
     path("dashboard_view", dashboard_view, name="dashboard_view"),
     


]