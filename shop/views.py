from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ItemForm, ReviewForm, AddressForm, OrderAddressForm, OrderPaymentShipmentForm
from .models import Item, Review, Address, Order, OrderStack, Category
from accounts.models import Stack
from django.utils.translation import gettext as _
from datetime import datetime

#helper function to get items for index and search
def get_items(request):
  #fliter items by category if specified, if not, get all items
  if 'category' in request.GET:
    cat = request.GET['category']
    try:
      c = Category.objects.get(id=cat)
      items = c.items
    except:items = Item.objects
  else:
    cat = 0
    items = Item.objects

  #set sorts codes
  sorts = [
    ['-created_at', _('Date created, descending')],
    ['created_at', _('Date created, ascending')],
    ['-price', _('Price, descending')],
    ['price', _('Price, ascending')],
  ]

  #sort items
  if 'sort' in request.GET and request.GET['sort'] in [x[0] for x in sorts]:
        items = items.all().order_by(request.GET['sort'])
        sort = request.GET['sort']
  else:
        items = items.all().order_by('-created_at')
        sort = '-created_at'


  #filter by query
  q = request.GET.get("query", "")
  items = items.filter(name__icontains=q)


  #split items into pages, get the current page number
  p_num = request.GET.get('page', 1)
  items = Paginator(items, 40)

  return [items, p_num, cat, sort, sorts, q]




def index(request):
  #get info from helper function
  items, p_num, cat, sort, sorts, q = get_items(request)

  #fill in context and render template
  context = {'items': items.page(p_num), 'cats': Category.objects.all(), 'cur': int(cat), 'sort': sort, 'sorts': sorts}
  return render(request, 'shop/index.html', context)

@login_required
def create_item(request):
  #if form filled in
  if request.method == "POST":
    form = ItemForm(request.POST, files=request.FILES)

    #if form is ok, then save item and redirect to the created item (if not rerender the same page with errors)
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
    #if form not filled in yet
    form = ItemForm()
  context = {'form': form,}
  return render(request, 'shop/create_item.html', context=context)

@login_required
def edit_item(request, item):
  #get the item and check permissions
  try:item = Item.objects.get(id=item)
  except:
    messages.error(request, _('Item not found'))
    return redirect('index')
  if (request.user.is_authenticated == False or item.author != request.user):
    return redirect('item', item=item.id)
  
  #same logic as item creation
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
  #get item or 404
  try:item = Item.objects.get(id=item)
  except:
    messages.error(request, _('Item not found'))
    return redirect('index')

  #if the user is submitting a review
  if request.method == "POST":
    form = ReviewForm(request.POST)

    #if the form is ok then save the review
    if form.is_valid():
      review = form.save(commit=False)
      review.author = request.user
      review.item = item
      review.save()
      messages.success(request, _('Review saved'))
      return redirect('view_item', item=item.id)
  else:
    #if hes not submitting a review, then prep an empty reivew form
    form = ReviewForm()

  #if there are more than 5 reviews, a link to "show all reviews" will appear
  more_reviews = 0

  #get reivews
  reviews = Review.objects.filter(item=item).order_by('-created_at')
  if len(reviews) > 0:
    reviews = [x for x in reviews if len(x.text) > 0 or x.author == request.user]
    if len(reviews) > 5:
      reviews = reviews[:5]
      more_reviews = True

  #check if the item is in users cart or not (needed in template)
  if request.user.is_authenticated and len(request.user.profile.cart.filter(id=item.id)) > 0:incart = True
  else:incart = False

  #fill in template and render it
  context = {'form': form,'item': item, 'incart':incart, 'reviews':reviews, 'more_reviews': more_reviews}
  return render(request, 'shop/view_item.html', context=context)

def item_reviews(request, item):
  #get the item
  try:item = Item.objects.get(id=item)
  except:
    messages.error(request, _('Item not found'))
    return redirect('index')
  
  #get reviews for the item
  reviews = Review.objects.filter(item=item).order_by('-created_at')

  #fill in and render
  context = {'item': item, 'reviews':reviews}
  return render(request, 'shop/item_reviews.html', context=context)


def delete_item_confirm(request, item):
  #get the item
  try:item = Item.objects.get(id=item)
  except:
    messages.error(request, _('Item not found'))
    return redirect('index')

  #check if the user has permissions to do this
  if (request.user.is_authenticated == False or item.author != request.user):
    return redirect('item', item=item.id)

  #confirm
  context = {'item': item,}
  return render(request, 'shop/delete_item_confirm.html', context=context)

def delete_item(request, item):
  #get item, check permissions and delete item if all is ok
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
  #get users cart; all information is gathered directly inside of the template from the "user" variable
  return render(request, "shop/cart.html")

@login_required
def cart_number(request, item):
  #update the number of items of a certain item in cart
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
  #if already checked
  if request.method == 'POST':
    #get item and remove it form current users cart
    try:item = request.user.profile.cart.get(id=item)
    except:return redirect('cart')
    request.user.profile.cart.remove(item)
    messages.success(request, _('Item removed from cart'))
    return redirect('cart')
  

  #if not already checked (that means method == GET), generate a check
  try:item = request.user.profile.cart.get(id=item)
  except:return redirect('cart')

  context = {'item': item}

  return render(request, 'shop/cart_remove_confirm.html', context=context)

@login_required
def cart_add(request, item=None):
  #add an item to cart if it exists
  try:item = Item.objects.get(id=item)
  except:
    messages.error(request, _('Item not found'))
    return redirect('index')
  request.user.profile.cart.add(item)
  messages.success(request, _('Item added to cart'))
  return redirect('cart')
 

@login_required
def buy(request):
  #generate an order
  order = Order(user=request.user)
  order.save()
  for item in request.user.profile.stack_set.all():
    #transform stacks to orderstacks
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

  #fill in and render
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
  #try to get the review and item
  try:review = request.user.review_set.get(id=review)
  except:
    messages.error(request, _('Review not found'))
    return redirect('index')

  try:item = Item.objects.get(id=item)
  except:
    messages.error(request, _('Item not found'))
    return redirect('index')

  #if review already checked
  if request.method == 'POST':
    #delete it
    try:
      if not item.review_set.filter(id=review.id).exists():
        return redirect('view_item', item=item.id)

      if request.user.review_set.filter(id=review.id).exists():
        review.delete()
    
    #if error, then redirect to index
    except:
      messages.error(request, _('An error occured when deleting your review'))
      return redirect('index')

    #redirect to the item
    messages.success(request, _('Review deleted!'))
    return redirect('view_item', item=item.id)


  #if not checked, than generate check
  context = {'item': item, 'review': review}
  return render(request, 'shop/review_delete.html', context=context)
  
@login_required
def review_edit(request, item, review):
  #get review and item
  try:review = request.user.review_set.get(id=review)
  except:
    messages.error(request, _('Review not found'))
    return redirect('index')
  try:item = Item.objects.get(id=item)
  except:
    messages.error(request, _('Item not found'))
    return redirect('index')

  #check permission
  if not (item.review_set.filter(id=review.id).exists() and review.author == request.user):
    messages.error(request, _('You don\'t have the permission to do that'))
    return redirect('item', item=item.id)
  
  #if filled in
  if request.method == "POST":
    form = ReviewForm(request.POST, files=request.FILES, instance=review)
    if form.is_valid():
      review = form.save()
      messages.success(request, _('Review updated'))
      return redirect('view_item', item=item.id)
  else:
    #if not, create form with the original review
    form = ReviewForm(instance=review)

  #fill in and render
  context = {'item': item, 'review': review, 'form': form}
  return render(request, 'shop/review_edit.html', context=context)

def search(request):
  if request.method != "GET":return redirect('index')
  
  #get info, fill in, render
  items, p_num, cat, sort, sorts, q = get_items(request)
  context = {'items': items.page(p_num), "q": q, 'cats': Category.objects.all(), 'cur': int(cat), 'sort': sort, 'sorts': sorts}
  return render(request, 'shop/search.html', context)

@login_required
def address(request):
  #get addresses and pass them to template
  addresses = request.user.address_set.all()
  stuff_for_render = {'addresses': addresses}
  return render(request, 'shop/address.html', context=stuff_for_render)

@login_required
def address_add(request):
  #same logic as with items and reviews
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
  #same logic as with items and reviews
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
  #same logic as with items and reviews
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
