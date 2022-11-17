from django.conf.urls import url, include
from api.v9.openingStockDetails import views


urlpatterns = [
    url(r'^create-openingStockDetails/$', views.create_openingStockDetails,
        name='create_openingStockDetails'),
    url(r'^list/openingStockDetails/$', views.list_openingStockDetailss,
        name='list_openingStockDetailss'),
    url(r'^view/openingStockDetails/(?P<pk>.*)/$',
        views.openingStockDetails, name='openingStockDetails'),
    url(r'^edit/openingStockDetails/(?P<pk>.*)/$',
        views.edit_openingStockDetails, name='edit_openingStockDetails'),
    url(r'^delete/openingStockDetails/(?P<pk>.*)/$',
        views.delete_openingStockDetails, name='delete_openingStockDetails'),

    url(r'^create-openingStockDetailsDummy/$',
        views.create_openingStockDetailsDummy, name='create_openingStockDetailsDummy'),
    url(r'^list/openingStockDetailsDummy/$',
        views.list_openingStockDetailsDummy, name='list_openingStockDetailsDummy'),
    url(r'^edit/openingStockDetailsDummy/(?P<pk>.*)/$',
        views.edit_openingStockDetailsDummy, name='edit_openingStockDetailsDummy'),
    url(r'^delete/openingStockDetailsDummy/(?P<pk>.*)/$',
        views.delete_openingStockDetailsDummy, name='delete_openingStockDetailsDummy'),

    url(r'^create-DummyforEditOpeningStock/$',
        views.create_DummyforEditOpeningStock, name='create_DummyforEditOpeningStock'),
]
