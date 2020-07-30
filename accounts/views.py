from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from .forms import (
  CustomUserCreationForm,
  ProfileForm, 
  UserEditForm, 
  )
from django.contrib.auth.models import User

# Create your views here.
def register_page(request):
  if request.method == "POST":
    form = CustomUserCreationForm(request.POST)
    profile_form = ProfileForm(request.POST)

    if form.is_valid() and profile_form.is_valid():
      user = form.save()

      profile = profile_form.save(commit=False)
      profile.user = user
      profile.save()

      user = authenticate(
        username=form.cleaned_data['username'], 
        password=form.cleaned_data['password1']
      )
      login(request, user)

      messages.success(request, _('Registration complete'))
      if 'next' in request.POST:return redirect(request.POST['next'])
      return redirect('user_profile')

  else:
    form = CustomUserCreationForm()
    profile_form = ProfileForm()
  context = {'form': form, 'profile_form': profile_form}
  return render(request, 'registration/register.html', context=context)

@login_required
def edit_profile_page(request):
  if (request.method == "POST"):
    user_form = UserEditForm(request.POST, instance=request.user)
    profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
    if user_form.is_valid() and profile_form.is_valid():
      user_form.save()
      profile_form.save()
      messages.success(request, _('Profile saved'))
      return redirect('user_profile')
  else:
    user_form = UserEditForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)
  context = {'form':user_form, 'profile_form':profile_form}
  return render(request, 'registration/change.html', context=context)
  
def show_profile(request, username=None):
  if not username:
    if request.user.is_authenticated:
      username = request.user.username
      return redirect(request.path + username)
    else:
      response = redirect('login')
      response['Location'] += '?next={}'.format(request.path)
      return response
  
  if request.user.is_authenticated and username == request.user.username:
    usr = request.user
  else:
    try:usr = User.objects.get(username=username)
    except:
      messages.error(request, _('Profile not found'))
      return redirect('index')
  
  if usr != request.user and usr.profile.profile_private == True:
    messages.error(request, _('Cannot show a private profile'))
    return redirect('index')
  reviews = usr.review_set.all().order_by('-created_at')
  items = usr.item_set.all().order_by('-created_at')
  context = {'usr': usr,'items':items, 'reviews':reviews}
  return render(request, 'registration/profile.html', context=context)
