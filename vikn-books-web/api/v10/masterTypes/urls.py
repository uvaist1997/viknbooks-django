from django.conf.urls import url, include
from api.v10.masterTypes import views


urlpatterns = [
    url(r'^create-masterType/$', views.create_masterType, name='create_masterType'),
    url(r'^masterTypes/$', views.masterTypes, name='masterTypes'),
    url(r'^view/masterType/(?P<pk>.*)/$', views.masterType, name='masterType'),
    url(r'^edit/masterType/(?P<pk>.*)/$',
        views.edit_masterType, name='edit_masterType'),
    url(r'^delete/masterType/(?P<pk>.*)/$',
        views.delete_masterType, name='delete_masterType'),
]
