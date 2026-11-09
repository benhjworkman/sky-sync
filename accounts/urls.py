from . import views
from django.urls import path

urlpatterns = [
    path('register_now', views.register_now, name="register_now"),
    path('login_user', views.login_user, name="login"),
    path('logout_user', views.logout_user, name="logout"),
    path('register_customer', views.register_customer, name="register_customer"),
    path('register_airline', views.register_airline, name="register_airline"),
]
