from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter
from . import views
urlpatterns = [
   url(r'^usernames/(?P<username>\w{5,20})/count/$',views.UsernameCountView.as_view()),
   url(r'^mobiles/(?P<mobile>1[3-9]\d{9}/count/$)',views.MobileCountView.as_view()),
    url(r'^authorizations/$',obtain_jwt_token),
   url('users/',views.UserCreateView.as_view()),
   url(r'^user/$',views.UserDetailView.as_view()),
    url(r'^emails/$',views.EmailView.as_view()),
    url(r'^emails/verification/$',views.EmailActiveView.as_view()),
    url(r'^browse_histories/$', views.BrowseHistoryView.as_view()),


]

router= DefaultRouter()
router.register('addresses',views.AddressViewSet,base_name='addresses')
urlpatterns += router.urls