from django.conf.urls import url   # A function that takes a prefix, and an arbitrary number of URL patterns,
# and returns a list of URL patterns in the format Django needs.
from django.urls import path

# from .views import LoginView # Importing Views that are define in a views.py
# from .views import LoginView, CreateUserAPIView
from . import views

urlpatterns = [
    # url(r'^$', views.signup),
    # url(r'^signup/$', views.signup, name='signup'),
    # path('log_me/', views.log_me, name='log_me'),
    # path('log_user/', views.logins, name='log_user'),
    # path('user_token/$', views.login, name='login'),
    # url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
    # path('/user1', views.home, name='home'),         # For a home page
    # path('register/', ProfileList.as_view()),
    # path('register1/', ProfileDetail.as_view()),
    # url(r'^create/$', CreateUserAPIView.as_view()),  # For a Register Page
    # url(r'^obtain_token/$', LoginView.as_view(),name='user_login'),   # For a Login Page




]
