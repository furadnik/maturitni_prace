from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import Profile, Stack

class CustomUserCreationForm(UserCreationForm):
  password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}), label=_("Password"))
  password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}), label=_("Password again"))
  
  class Meta:
    model = User
    fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    localized_fields = '__all__'
    widgets = {
      'username': forms.TextInput(attrs={'class':'form-control'}),
      'email': forms.TextInput(attrs={'class':'form-control'}),
      'first_name': forms.TextInput(attrs={'class':'form-control'}),
      'last_name':  forms.TextInput(attrs={'class':'form-control'}),

    }

  def save(self, commit=True):
    user = super().save(commit=False)

    user.email = self.cleaned_data['email']
    user.first_name = self.cleaned_data['first_name']
    user.last_name = self.cleaned_data['last_name']

    if commit:user.save()
    return user

class ProfileForm(forms.ModelForm):
  class Meta:
    model = Profile
    exclude = ('user','cart')
    localized_fields = '__all__'
    widgets = {
      'profile_pic': forms.FileInput(attrs={'class':'form-control-file'}),
      'profile_private': forms.CheckboxInput(attrs={'class':'form-check-input ml-1'}),
      'full_name_private': forms.CheckboxInput(attrs={'class':'form-check-input ml-1'}),
      'reviews_list_private': forms.CheckboxInput(attrs={'class':'form-check-input ml-1'}),
      'email_private': forms.CheckboxInput(attrs={'class':'form-check-input ml-1'}),
      'twitter': forms.TextInput(attrs={'class':'form-control w-50'}),
      'instagram': forms.TextInput(attrs={'class':'form-control w-50'}),
      'facebook': forms.TextInput(attrs={'class':'form-control w-50'})
    }
    labels = {
      'profile_pic': _("Profile picture"),
      'profile_private': _("Profile private"),
      'full_name_private': _("Full name private"),
      'reviews_list_private': _("Reviews list private"),
      'email_private': _("E-mail private"),
    }

class UserEditForm(forms.ModelForm):

  class Meta:
    model = User
    fields = ('first_name', 'last_name', 'email')
    localized_fields = '__all__'
    widgets = {
      "first_name": forms.TextInput(attrs={'class':'form-control w-50'}),
      'last_name': forms.TextInput(attrs={'class':'form-control w-50'}),
      'email': forms.TextInput(attrs={'class':'form-control w-50'}),
    }

class NumberChangeForm(forms.ModelForm):
  class Meta:
    model = Stack
    fields = ('number',)
