from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.home, name='home'),
    re_path(r'^signup$', views.signup, name="signup"),
    re_path(r"^signup/validate$", views.signup_validate, name="signup_validate"),
    re_path(r'^login$', views.c_login, name="login"),
    re_path(r'^login/send_otp$', views.send_otp, name="send_otp"),
    re_path(r"^login/validate$", views.login_validate, name="login_validate"),
    re_path(r'^search$', views.search, name="search"),
    re_path(r'country/(?P<country_name>[\w|\W]+)$', views.get_country_details, name="country_page"),
    re_path(r'^logout$', views.c_logout, name="logout"),
]
