from django.conf.urls import url, include
from api.v5.posholds import views


urlpatterns = [
    url(r'^create-poshold/$', views.create_poshold, name='create_poshold'),
    url(r'^edit/poshold/(?P<pk>.*)/$', views.edit_poshold, name='edit_poshold'),
    url(r'^list/posholdMaster/$', views.list_posholdMaster,
        name='list_posholdMaster'),
    url(r'^view/posholdMaster/(?P<pk>.*)/$',
        views.posholdMaster, name='posholdMaster'),
    url(r'^delete/posholdDetails/(?P<pk>.*)/$',
        views.delete_posholdDetails, name='delete_posholdDetails'),
    url(r'^delete/posholdMaster/(?P<pk>.*)/$',
        views.delete_posholdMaster, name='delete_posholdMaster'),
]
