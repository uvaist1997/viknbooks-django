from django.conf.urls import url, include
from api.v5.userTypes import views


urlpatterns = [
    url(r'^create-user-type/$', views.create_user_type, name='create_user_type'),
    url(r'^user-types/$', views.user_types, name='user_types'),
    url(r'^view/brand/(?P<pk>.*)/$', views.brand, name='brand'),
    url(r'^edit/brand/(?P<pk>.*)/$', views.edit_brand, name='edit_brand'),
    url(r'^delete/brand/(?P<pk>.*)/$', views.delete_brand, name='delete_brand'),
]
