from django.conf.urls import url, include
from api.v10.kitchen import views


urlpatterns = [
    url(r'^create-kitchen/$', views.create_kitchen, name='create_kitchen'),
    url(r'^kitchens/$', views.kitchens, name='kitchens'),
    url(r'^view/kitchen/(?P<pk>.*)/$', views.kitchen, name='kitchen'),
    url(r'^edit/kitchen/(?P<pk>.*)/$', views.edit_kitchen, name='edit_kitchen'),
    url(r'^delete/kitchen/(?P<pk>.*)/$',
        views.delete_kitchen, name='delete_kitchen'),
]
