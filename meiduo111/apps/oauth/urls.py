from django.conf.urls import url,include
from django.contrib import admin

from . import views

urlpatterns = [
    url('^qq/authorization/$',views.QQurlView.as_view()),
    url('^qq/user/$',views.QQLoginView.as_view()),
   ]