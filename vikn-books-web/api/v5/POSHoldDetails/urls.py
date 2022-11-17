from django.conf.urls import url, include
from api.v5.POSHoldDetails import views


urlpatterns = [
    url(r'^create-posholdDetails/$', views.create_posholdDetails,
        name='create_posholdDetails'),
    url(r'^list/posholdDetails/$', views.list_posholdDetails,
        name='list_posholdDetails'),
    url(r'^view/posholdDetails/(?P<pk>.*)/$',
        views.posholdDetails, name='posholdDetails'),
    url(r'^edit/posholdDetails/(?P<pk>.*)/$',
        views.edit_posholdDetails, name='edit_posholdDetails'),
    url(r'^delete/posholdDetails/(?P<pk>.*)/$',
        views.delete_posholdDetails, name='delete_posholdDetails'),

    url(r'^create-POSHoldDetailsDummy/$', views.create_POSHoldDetailsDummy,
        name='create_POSHoldDetailsDummy'),
    url(r'^list/POSHoldDetailsDummy/$', views.list_POSHoldDetailsDummy,
        name='list_POSHoldDetailsDummy'),
    url(r'^edit/POSHoldDetailsDummy/(?P<pk>.*)/$',
        views.edit_POSHoldDetailsDummy, name='edit_POSHoldDetailsDummy'),
    url(r'^delete/POSHoldDetailsDummy/(?P<pk>.*)/$',
        views.delete_POSHoldDetailsDummy, name='delete_POSHoldDetailsDummy'),

    url(r'^create-DummyforEditPosHoldMaster/$',
        views.create_DummyforEditPosHoldMaster, name='create_DummyforEditPosHoldMaster'),
]
