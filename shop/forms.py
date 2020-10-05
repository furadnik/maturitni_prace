from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Item, Review, Address, Order, Category

class ItemForm(forms.ModelForm):
  categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), widget=forms.CheckboxSelectMultiple)
  class Meta:
    model = Item
    fields = ('name', 'price', 'description', 'image')
    localized_fields = '__all__'
    widgets = {
      'image': forms.FileInput(attrs={'class':'form-control-file'}),
      'name': forms.TextInput(attrs={'class':'form-control'}),
      'price': forms.TextInput(attrs={'class':'form-control', 'type': 'number'}),
      'description': forms.Textarea(attrs={'class':'form-control'}),
    }
    labels = {
      'image': _('Image'),
      'name': _('Name'),
      'price': _('Price'),
      'description': _('Description'),
    }

class ReviewForm(forms.ModelForm):
  class Meta:
    model = Review
    fields = ('stars', 'text')
    localized_fields = '__all__'
    widgets = {
      'stars': forms.Select(attrs={'class':'form-control'}),
      'text': forms.Textarea(attrs={'class':'form-control'}),
    }
    labels = {
      'stars': _('Stars'),
      'text': _('Text'),
    }

class AddressForm(forms.ModelForm):
  class Meta:
    model = Address
    exclude = ('user',)
    labels = {
      "first_name": _("First name"),
      "last_name": _("Last name"),
      "avenue": _("Avenue"),
      "post_code": _("Postal code"),
      "city": _("City"),
    }
    widgets = {
      "first_name":forms.TextInput(attrs={'class':'form-control'}),
      "last_name": forms.TextInput(attrs={'class':'form-control'}),
      "avenue": forms.TextInput(attrs={'class':'form-control'}),
      "post_code": forms.TextInput(attrs={'class':'form-control'}),
      "city": forms.TextInput(attrs={'class':'form-control'}),
    }

class OrderPaymentShipmentForm(forms.ModelForm):
  SHIPMENT_OPTIONS = [('post', _('Post')), ('dpd', _('DPD')), ('ppl', _('PPL'))]
  PAYMENT_OPTIONS = [('on_del', _('On Delivery')), ('paypal', _('PayPal')), ('ccard', _('CreditCard'))]

  payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_OPTIONS, label=_('Payment'))
  shipment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=SHIPMENT_OPTIONS, label=_('Shipment'))

  class Meta:
    model = Order
    fields = ('payment_option', 'shipment_option')

class OrderAddressForm(forms.ModelForm):
  def __init__(self, user,*args,**kwargs):
    super (OrderAddressForm,self ).__init__(*args,**kwargs) # populates the post
    self.fields['address'].queryset = Address.objects.filter(user=user)
    self.fields['address'].required = True
    self.fields['address'].empty_label = None
  class Meta:
    model = Order
    fields = ('address',)
    widgets = {'address': forms.RadioSelect}
    labels = {'address': _('Address')}