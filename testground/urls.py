from django.urls import path

from . import views

urlpatterns = [
    # path('hello/', views.say_hello),
    path('', views.home, name="home"),
    path('signup', views.signup, name="signup"),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('signin', views.signin, name="signin"),
    path('signout', views.signout, name="signout"),
]