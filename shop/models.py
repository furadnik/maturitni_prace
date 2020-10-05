import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from PIL import Image

# Create your models here.
class Item(models.Model):
  author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
  price = models.fields.FloatField(validators=[MinValueValidator(1.0),])
  name = models.fields.CharField(max_length=60)
  created_at = models.DateTimeField(auto_now_add=True)
  id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
  description = models.fields.TextField(blank=True, max_length=1000)
  image = models.ImageField(
    default="shop/item_imgs/def.png", 
    upload_to="shop/item_imgs",
    blank=True
    )
  def __str__(self):
    return str(self.name)

  @property
  def rating(self):
    c = self.review_set.count()
    a = 0
    for x in self.review_set.all().values_list('stars', flat=True):a+=x
    if c == 0:return 0
    r = a/c
    return r

  @property
  def rating_stars(self):
    r = ""
    for _ in range(round(self.rating)):r += '&#11088;'
    return r

  def save(self):
    #self.id = self.name.lower().replace(' ', '_').replace('/', '')
    super().save()
    img = Image.open(self.image.path)
    treshold = 300
    img.thumbnail((treshold, treshold))
    size = img.size
    if size[0] > size[1]:size = (size[1], size[1])
    else:size = (size[0], size[0])
    background = Image.new('RGB', size, (255, 255, 255, 0))
    background.paste(
        img, (int((size[0] - img.size[0]) / 2), int((size[1] - img.size[1]) / 2))
    )
    if size[0] < 300:
      background = background.resize((300, 300))
    background.save(self.image.path)

class Review(models.Model):
  NUM_STARS = [
    (1, '1 star'),
    (2, '2 stars'),
    (3, '3 stars'),
    (4, '4 stars'),
    (5, '5 stars'),
  ]
  author = models.ForeignKey(User, on_delete=models.CASCADE)
  item = models.ForeignKey(Item, on_delete=models.CASCADE)
  stars = models.fields.IntegerField(choices=NUM_STARS, default=5)
  text = models.fields.TextField(null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 

  @property
  def stars_rendered(self):
    r = ""
    for _ in range(self.stars):r += '&#11088;'
    return r

  def __str__(self):
    return str(self.item.name) + " Review"

class Address(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  first_name = models.CharField(max_length=100)
  last_name = models.CharField(max_length=100)
  avenue = models.CharField(max_length=100)
  post_code = models.IntegerField()
  city = models.CharField(max_length=100)
  id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 

  def __str__(self):
    return f'{self.first_name} {self.last_name}, {self.avenue}, {self.post_code} {self.city}'

class Order(models.Model):
  SHIPMENT_OPTIONS = [('post', _('Post')), ('dpd', _('DPD')), ('ppl', _('PPL'))]
  PAYMENT_OPTIONS = [('on_del', _('On Delivery')), ('paypal', _('PayPal')), ('ccard', _('CreditCard'))]

  user = models.ForeignKey(User, on_delete=models.CASCADE)
  items = models.ManyToManyField(Item, through='OrderStack', related_name='order_stack_set')
  address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
  shipment_option = models.CharField(max_length=4, null=True, choices=SHIPMENT_OPTIONS)
  payment_option = models.CharField(max_length=6, null=True, choices=PAYMENT_OPTIONS)
  id = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False) 
  done = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True, null=True)
  confirmed_at = models.DateTimeField(null=True)
  shipped = models.BooleanField(default=False)
  shipped_at = models.DateTimeField(null=True)

  def __str__(self):
    return f'{self.user.username} - {len(self.items.all())} items ({self.created_at})'

class OrderStack(models.Model):
  order = models.ForeignKey(Order, on_delete=models.CASCADE)
  item = models.ForeignKey(Item, on_delete=models.CASCADE)
  number = models.fields.IntegerField(default=1)

  @property
  def total_price(self):
    return self.number*self.item.price

class Category(models.Model):
  name = models.CharField(max_length=30)
  items = models.ManyToManyField(Item, related_name="categories")

  def __str__(self):
    return self.name