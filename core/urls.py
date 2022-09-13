from django.contrib.auth import views as auth_views
from django.urls import path 

from . import views

urlpatterns = [
    path('', views.frontpage, name='frontpage'),
    path('microsoft-signin', views.sign_in, name='signin'),
    path('microsoft-signout', views.sign_out, name='signout'),
    path('callback/', views.callback, name='callback'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', views.sign_out, name='logout'),
]