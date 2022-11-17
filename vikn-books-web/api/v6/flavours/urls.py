from django.conf.urls import url, include
from api.v6.flavours import views


urlpatterns = [
    url(r'^create-flavour/$', views.create_flavour, name='create_flavour'),
    url(r'^flavours/$', views.flavours, name='flavours'),
    url(r'^view/flavour/(?P<pk>.*)/$', views.flavour, name='flavour'),
    url(r'^edit/flavour/(?P<pk>.*)/$', views.edit_flavour, name='edit_flavour'),
    url(r'^delete/flavour/(?P<pk>.*)/$',
        views.delete_flavour, name='delete_flavour'),
]
