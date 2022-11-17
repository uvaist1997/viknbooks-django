from django.conf.urls import url, include
from api.v8.POSHoldMaster import views


urlpatterns = [
    url(r'^create-posholdMaster/$', views.create_posholdMaster,
        name='create_posholdMaster'),
    url(r'^list/posholdMaster/$', views.list_posholdMaster,
        name='list_posholdMaster'),
    url(r'^view/posholdMaster/(?P<pk>.*)/$',
        views.posholdMaster, name='posholdMaster'),
    url(r'^edit/posholdMaster/(?P<pk>.*)/$',
        views.edit_posholdMaster, name='edit_posholdMaster'),
    url(r'^delete/posholdMaster/(?P<pk>.*)/$',
        views.delete_posholdMaster, name='delete_posholdMaster'),
]
