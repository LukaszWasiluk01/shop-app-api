from django.urls import include, path
from users import views

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterUserView.as_view(), name="register"),
    path("", include("dj_rest_auth.urls")),
]
