from django.conf.urls import url,include
from django.contrib import admin
from . import views
from rest_framework.routers import DefaultRouter
urlpatterns = [

]

router= DefaultRouter()
router.register('areas',views.AreaViewSet,base_name='areas')
urlpatterns += router.urls