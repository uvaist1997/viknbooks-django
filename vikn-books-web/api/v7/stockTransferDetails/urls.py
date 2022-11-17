from django.conf.urls import url, include
from api.v7.stockTransferDetails import views


urlpatterns = [
    url(r'^create-stockTransferDetails/$',
        views.create_stockTransferDetails, name='create_stockTransferDetails'),
    url(r'^list/stockTransferDetails/$', views.list_stockTransferDetails,
        name='list_stockTransferDetails'),
    url(r'^view/stockTransferDetails/(?P<pk>.*)/$',
        views.stockTransferDetails, name='stockTransferDetails'),
    url(r'^edit/stockTransferDetails/(?P<pk>.*)/$',
        views.edit_stockTransferDetails, name='edit_stockTransferDetails'),
    url(r'^delete/stockTransferDetails/(?P<pk>.*)/$',
        views.delete_stockTransferDetails, name='delete_stockTransferDetails'),

    url(r'^create-stockTransferDetailsDummy/$',
        views.create_stockTransferDetailsDummy, name='create_stockTransferDetailsDummy'),
    url(r'^list/stockTransferDetailsDummy/$',
        views.list_stockTransferDetailsDummy, name='list_stockTransferDetailsDummy'),
    url(r'^edit/stockTransferDetailsDummy/(?P<pk>.*)/$',
        views.edit_stockTransferDetailsDummy, name='edit_stockTransferDetailsDummy'),
    url(r'^delete/stockTransferDetailsDummy/(?P<pk>.*)/$',
        views.delete_stockTransferDetailsDummy, name='delete_stockTransferDetailsDummy'),

    url(r'^create-DummyforEditStockTransferMaster/$',
        views.create_DummyforEditStockTransferMaster, name='create_DummyforEditStockTransferMaster'),
]
