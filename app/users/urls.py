from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from users import views

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterUserView.as_view(), name="register"),
    path("me/", views.ManageUserView.as_view(), name="me"),
    path("obtain-token/", obtain_auth_token, name="obtain-token"),
]
