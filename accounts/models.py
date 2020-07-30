from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from shop.models import Item

class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  profile_pic = models.ImageField(
    default="accounts/profile_pics/def.png", upload_to="accounts/profile_pics",
    blank=True,
    )
  cart = models.ManyToManyField(Item, through='Stack')

  profile_private = models.BooleanField(default=False)
  full_name_private = models.BooleanField(default=False)
  reviews_list_private = models.BooleanField(default=False)
  email_private = models.BooleanField(default=False)

  twitter = models.CharField(max_length=100, blank=True)
  instagram = models.CharField(max_length=100, blank=True)
  facebook = models.CharField(max_length=100, blank=True)

  @property
  def total_price(self):
    items = self.stack_set.all()
    r = 0.0
    for x in items:
      r += x.total_price
    return r

  def __str__(self):
    return self.user.username

  def save(self):
    super().save()
    img = Image.open(self.profile_pic.path)
    treshold = 300
    img.thumbnail((treshold, treshold))
    size = img.size
    background = Image.new('RGBA', size, (255, 255, 255, 0))
    background.paste(
        img, (int((size[0] - img.size[0]) / 2), int((size[1] - img.size[1]) / 2))
    )
    background.save(self.profile_pic.path)

class Stack(models.Model):
  item = models.ForeignKey(Item, on_delete=models.CASCADE)
  user = models.ForeignKey(Profile, on_delete=models.CASCADE)
  number = models.fields.IntegerField(default=1)
  
  def __str__(self):
    return str(self.user.user.username) + ": " + str(self.item.name)

  @property
  def total_price(self):
    return self.number*self.item.price

