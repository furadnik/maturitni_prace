from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ItemForm, ReviewForm, AddressForm, OrderAddressForm, OrderPaymentShipmentForm
from .models import Item, Review, Address, Order, OrderStack, Category
from accounts.models import Stack
from django.utils.translation import gettext as _
from datetime import datetime

# Create your views here.
def index(request):
  if 'category' in request.GET:
    cat = request.GET['category']
    try:
      c = Category.objects.get(id=cat)
      items = c.items
    except:items = Item.objects
  else:
    cat = 0
    items = Item.objects

  sorts = [
    ['-created_at', _('Date created, descending')],
    ['created_at', _('Date created, ascending')],
    ['-price', _('Price, descending')],
    ['price', _('Price, ascending')],
  ]

  if 'sort' in request.GET and request.GET['sort'] in [x[0] for x in sorts]:
        items = items.all().order_by(request.GET['sort'])
        sort = request.GET['sort']
  else:
        items = items.all().order_by('-created_at')
        sort = '-created_at'

  p_num = request.GET.get('page', 1)
  items = Paginator(items, 40)

  context = {'items': items.page(p_num), 'cats': Category.objects.all(), 'cur': int(cat), 'sort': sort, 'sorts': sorts}
  return render(request, 'shop/index.html', context)

@login_required
def create_item(request):
  if request.method == "POST":
    form = ItemForm(request.POST, files=request.FILES)

    if form.is_valid():
      item = form.save(commit=False)
      item.author = request.user
      item.save() #first save the item w/o cats, then add them and save again bcs database n stuff
      if "categories" in form.cleaned_data:
            item.categories.set(form.cleaned_data["categories"])
            item.save()
      messages.success(request, _('Item created'))
      return redirect('view_item', item=item.id)
  else:
    form = ItemForm()
  context = {'form': form,}
  return render(request, 'shop/create_item.html', context=context)

@login_required
def edit_item(request, item):
  try:item = Item.objects.get(id=item)
  except:
    messages.error(request, _('Item not found'))
    return redirect('index')
  if (request.user.is_authenticated == False or item.author != request.user):
    return redirect('item', item=item.id)
  
  if request.method == "POST":
    form = ItemForm(request.POST, files=request.FILES, instance=item)

    if form.is_valid():
      item = form.save()
      if "categories" in form.cleaned_data:
            item.categories.set(form.cleaned_data["categories"])
            item.save()
      messages.success(request, _('Item saved'))
      return redirect('view_item', item=item.id)
  else:
    form = ItemForm(instance=item)
  context = {'form': form,'iid': item.id}
  return render(request, 'shop/create_item.html', context=context)

def view_item(request, item):
  try:item = Item.objects.get(id=item)
  except:
    messages.error(request, _('Item not found'))
    return redirect('index')
  if request.method == "POST":
    form = ReviewForm(request.POST)

    if form.is_valid():
      review = form.save(commit=False)
      review.author = request.user
      review.item = item
      review.save()
      messages.success(request, _('Review saved'))
      return redirect('view_item', item=item.id)
  else:
    form = ReviewForm()
  more_reviews = 0
  reviews = Review.objects.filter(item=item).order_by('-created_at')
  if len(reviews) > 0:
    reviews = [x for x in reviews if len(x.text) > 0 or x.author == request.user]
    if len(reviews) > 5:
      reviews = reviews[:5]
      more_reviews = True
  if request.user.is_authenticated and len(request.user.profile.cart.filter(id=item.id)) > 0:incart = True
  else:incart = False
  context = {'form': form,'item': item, 'incart':incart, 'reviews':reviews, 'more_reviews': more_reviews}
  return render(request, 'shop/view_item.html', context=context)

def item_reviews(request, item):
  try:item = Item.objects.get(id=item)
  except:
    messages.error(request, _('Item not found'))
    return redirect('index')
  reviews = Review.objects.filter(item=item).order_by('-created_at')
  context = {'item': item, 'reviews':reviews}
  return render(request, 'shop/item_reviews.html', context=context)


def delete_item_confirm(request, item):
  try:item = Item.objects.get(id=item)
  except:
    messages.error(request, _('Item not found'))
    return redirect('index')
  if (request.user.is_authenticated == False or item.author != request.user):
    return redirect('item', item=item.id)
  context = {'item': item,}
  return render(request, 'shop/delete_item_confirm.html', context=context)

def delete_item(request, item):
  try:item = Item.objects.get(id=item)
  except:
    messages.error(request, _('Item not found'))
    return redirect('index')
  if (request.user.is_authenticated == False or item.author != request.user):
    return redirect('item', item=item.id)
  if request.method == "POST":
    item.delete()
    messages.success(request, _('Item deleted'))
    return redirect('user_profile')
  else:return redirect('view_item', item=item.id)

@login_required
def cart(request):
  return render(request, "shop/cart.html")

@login_required
def cart_number(request, item):
  if request.method == "POST":
    try:stack = Stack.objects.get(id=request.POST["id"])
    except:return redirect('cart')
    if str(stack.item.id) == item:
      if int(request.POST["number"]) == 0:return redirect('cart_remove', item=item)
      stack.number = int(request.POST["number"])
      stack.save()
      messages.success(request, _('Cart updated'))
  return redirect('cart')

@login_required
def cart_remove(request, item=None):
  if request.method == 'POST':
    try:item = request.user.profile.cart.get(id=item)
    except:return redirect('cart')
    request.user.profile.cart.remove(item)
    messages.success(request, _('Item removed from cart'))
    return redirect('cart')
  
  try:item = request.user.profile.cart.get(id=item)
  except:return redirect('cart')

  context = {'item': item}

  return render(request, 'shop/cart_remove_confirm.html', context=context)

@login_required
def cart_add(request, item=None):
  try:item = Item.objects.get(id=item)
  except:
    messages.error(request, _('Item not found'))
    return redirect('index')
  request.user.profile.cart.add(item)
  messages.success(request, _('Item added to cart'))
  return redirect('cart')
 

@login_required
def buy(request):
  order = Order(user=request.user)
  order.save()
  for item in request.user.profile.stack_set.all():
    stack = OrderStack(order=order, item=item.item, number=item.number)
    stack.save()
  order.save()
  context = {'order': order}
  return render(request, 'shop/buy.html', context=context)
  
@login_required
def buy_details(request):
  #get the order by id
  try:
    if request.method == "POST":order = request.POST['order']
    else:order = request.GET['order']
    order = Order.objects.get(id=order)
  except:return redirect('buy')

  #if the form is filled out
  if request.method == 'POST':
    form = OrderPaymentShipmentForm(request.POST, instance=order)
    if form.is_valid():
      form.save()
      response = redirect('buy_address')
      response['Location'] += '?order=' + str(order.id)
      return response

  #if the form is not already filled out
  else:form = OrderPaymentShipmentForm(instance=order)

  #pass the form to template
  context = {'form': form, 'order': order}
  return render(request, 'shop/buy_details.html', context=context)

@login_required
def buy_address(request):
  #get the order by id
  try:
    if request.method == "POST":order = request.POST['order']
    else:order = request.GET['order']
    order = Order.objects.get(id=order)
  except:return redirect('buy')

  #if the form is filled out
  if request.method == 'POST':
    form = OrderAddressForm(request.user, request.POST, instance=order) #TODO ADDRESS FORM
    if form.is_valid():
      form.save()
      response = redirect('buy_confirm')
      response['Location'] += '?order=' + str(order.id)
      return response

  #if the form is not already filled out
  else:
    form = OrderAddressForm(request.user, instance=order)

  #pass the form to template
  context = {'form': form, 'order': order}
  return render(request, 'shop/buy_address.html', context=context)

@login_required
def buy_confirm(request):
  #get the order by id
  try:
    if request.method == "POST":order = request.POST['order']
    else:order = request.GET['order']
    order = Order.objects.get(id=order)
  except:return redirect('buy')

  context = {'order': order}
  return render(request, 'shop/buy_confirm.html', context=context)

@login_required
def buy_success(request):
  #get the order by id
  try:
    if request.method == "POST":order = request.POST['order']
    else:order = request.GET['order']
    order = Order.objects.get(id=order)
  except:return redirect('buy')

  #write to database
  request.user.profile.cart.clear()
  order.done = True
  order.confirmed_at = datetime.now()
  order.save()
  
  #write an email
  #

  #success message
  messages.success(request, _('Order created! Thanks for shopping'))
  
  return redirect('index') #message thanks for shopping
    

@login_required
def review_delete(request, item, review):
  if request.method == 'POST':
    try:review = request.user.review_set.get(id=review)
    except:
      messages.error(request, _('Review not found'))
      return redirect('index')
    try:item = Item.objects.get(id=item)
    except:
      messages.error(request, _('Item not found'))
      return redirect('index')

    try:
      if not item.review_set.filter(id=review.id).exists():
        return redirect('view_item', item=item.id)

      if request.user.review_set.filter(id=review.id).exists():
        review.delete()

    except:
      messages.error(request, _('An error occured when deleting your review'))
      return redirect('index')

    messages.success(request, _('Review deleted!'))
    return redirect('view_item', item=item.id)

  try:review = request.user.review_set.get(id=review)
  except:
    messages.error(request, _('Review not found'))
    return redirect('index')
  try:item = Item.objects.get(id=item)
  except:
    messages.error(request, _('Item not found'))
    return redirect('index')

  context = {'item': item, 'review': review}

  return render(request, 'shop/review_delete.html', context=context)
  
@login_required
def review_edit(request, item, review):
  try:review = request.user.review_set.get(id=review)
  except:
    messages.error(request, _('Review not found'))
    return redirect('index')
  try:item = Item.objects.get(id=item)
  except:
    messages.error(request, _('Item not found'))
    return redirect('index')

  if not (item.review_set.filter(id=review.id).exists() and review.author == request.user):
    messages.error(request, _('You don\'t have the permission to do that'))
    return redirect('item', item=item.id)
  
  if request.method == "POST":
    form = ReviewForm(request.POST, files=request.FILES, instance=review)
    if form.is_valid():
      review = form.save()
      messages.success(request, _('Review updated'))
      return redirect('view_item', item=item.id)
  else:
    form = ReviewForm(instance=review)

  context = {'item': item, 'review': review, 'form': form}
  return render(request, 'shop/review_edit.html', context=context)

def search(request):
  if request.method != "GET":return redirect('index')
  if 'category' in request.GET:
    cat = request.GET['category']
    try:
      c = Category.objects.get(id=cat)
      items = c.items
    except:items = Item.objects
  else:
    cat = 0
    items = Item.objects
  q = request.GET["query"]

  sorts = [
    ['-created_at', _('Date created, descending')],
    ['created_at', _('Date created, ascending')],
    ['-price', _('Price, descending')],
    ['price', _('Price, ascending')],
  ]

  if 'sort' in request.GET and request.GET['sort'] in [x[0] for x in sorts]:
        items = items.filter(name__icontains=q).order_by(request.GET['sort'])
        sort = request.GET['sort']
  else:
        items = items.filter(name__icontains=q).order_by('-created_at')
        sort = '-created_at'

  p_num = request.GET.get('page', 1)
  items = Paginator(items, 40)

  context = {'items': items.page(p_num), "q": q, 'cats': Category.objects.all(), 'cur': int(cat), 'sort': sort, 'sorts': sorts}
  return render(request, 'shop/search.html', context)

@login_required
def address(request):
  addresses = request.user.address_set.all()
  stuff_for_render = {'addresses': addresses}
  return render(request, 'shop/address.html', context=stuff_for_render)

@login_required
def address_add(request):
  if request.method == "POST":
    form = AddressForm(request.POST)
    if form.is_valid():
      address = form.save(commit=False)
      address.user = request.user
      address.save()
      messages.success(request, _('Address added!'))
      if 'next' in request.POST:return redirect(request.POST['next'])
      if 'order' in request.POST:
        res = redirect('buy_address')
        res['Location'] += '?order=' + request.POST['order']
        return res
      return redirect('address')
  else:
    form = AddressForm()
  stuff_for_render = {'form': form}
  return render(request, 'shop/address_add.html', context=stuff_for_render)

@login_required
def address_edit(request, id):
  try:address = Address.objects.get(id=id)
  except:
    messages.error(request,_('Address not found'))
    return redirect('address')
  if address.user != request.user:
    messages.error(request,_('You don\'t have permission to access that!'))
    return redirect('index')
  if request.method == "POST":
    form = AddressForm(request.POST, instance=address)
    if form.is_valid():
      form.save()
      messages.success(request, _('Address saved!'))
      if 'next' in request.POST:return redirect(request.POST['next'])
      return redirect('address')
  else:
    form = AddressForm(instance=address)
  stuff_for_render = {'form': form}
  return render(request, 'shop/address_edit.html', context=stuff_for_render)

@login_required
def address_delete(request, id):
  try:address = Address.objects.get(id=id)
  except:
    messages.error(request,'Address not found')
    return redirect('address')
  if address.user != request.user:
    messages.error(request,_('You don\'t have permission to access that!'))
  if request.method == "POST":
    address.delete()
    messages.success(request, _('Address deleted!'))
    return redirect('address') 
  stuff_for_render = {'address': address}
  return render(request, 'shop/address_delete.html', context=stuff_for_render)
