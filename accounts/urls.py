from django.urls import path#, reverse
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
  path('login/', auth_views.LoginView.as_view(), name="login"),
  path('logout', auth_views.LogoutView.as_view(), name="logout"),
  path('register/', views.register_page, name="register"),
  path(settings_url_pattern:='settings/', views.edit_profile_page, name="edit_profile"),
  path('profile/<str:username>/', views.show_profile, name="profile"),
  path('profile/', views.show_profile, name="user_profile"),

  path('password_reset/', auth_views.PasswordResetView.as_view(
    template_name="registration/pswdres1.html",
    ), name="password_reset"),

  path('password_change/', auth_views.PasswordChangeView.as_view(
    success_url='../'+settings_url_pattern,
    template_name='registration/password_change.html'
    ), name="password_change"),

  path('password_reset/sent/', auth_views.PasswordResetDoneView.as_view(
    template_name="registration/pswdres2_sent.html",
    ), name="password_reset_done"),

  path('password_reset/confirm/<uidb64>[0-9A-Za-z]+<token>', auth_views.PasswordResetConfirmView.as_view(
    template_name="registration/pswdres3_confirm.html",
    ), name="password_reset_confirm"),

  path('password_reset/success/', auth_views.PasswordResetCompleteView.as_view(
    template_name="registration/pswdres4_success.html",
    ), name="password_reset_complete"), 
]