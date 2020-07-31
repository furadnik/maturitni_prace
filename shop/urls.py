from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"), 
    path('create_item/', views.create_item, name="create_item"),  
    path('edit_item/<item>/', views.edit_item, name="edit_item"),  
    path('delete_item_confirm/<item>/', views.delete_item_confirm, name="delete_item_confirm"),  
    path('delete_item/<item>/', views.delete_item, name="delete_item"),  
    path('item/<item>/', views.view_item, name="view_item"), 
    path('item/<item>/reviews/', views.item_reviews, name="item_reviews"),
    path('cart/', views.cart, name="cart"), 
    path('cart/number/<item>/', views.cart_number, name="cart_number"), 
    path('search/', views.search, name="search"), 
    path('categories/', views.categories, name="categories"), 
    path('cart_add/<item>/', views.cart_add, name="cart_add"), 
    path('cart_remove/<item>/', views.cart_remove, name="cart_remove"), 
    path('buy/', views.buy, name="buy"),
    path('buy/details', views.buy_details, name="buy_details"),
    path('buy/address', views.buy_address, name="buy_address"),
    path('buy/confirm', views.buy_confirm, name="buy_confirm"),
    path('buy/success', views.buy_success, name="buy_success"),
    path('review_edit/<item>/<review>', views.review_edit, name="review_edit"), 
    path('review_delete/<item>/<review>', views.review_delete, name="review_delete"), 
    path('address/', views.address, name="address"),
    path('address/add', views.address_add, name="address_add"),
    path('address/delete/<id>', views.address_delete, name="address_delete"),
    path('address/edit/<id>', views.address_edit, name="address_edit"),
]