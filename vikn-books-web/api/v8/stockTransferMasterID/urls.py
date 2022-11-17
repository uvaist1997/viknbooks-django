from django.conf.urls import url, include
from api.v8.stockTransferMasterID import views


urlpatterns = [
    url(r'^create-stockTransferMasterID/$',
        views.create_stockTransferMasterID, name='create_stockTransferMasterID'),
    url(r'^list/stockTransferMasterID/$', views.list_stockTransferMasterID,
        name='list_stockTransferMasterID'),
    url(r'^view/stockTransferMasterID/(?P<pk>.*)/$',
        views.stockTransferMasterID, name='stockTransferMasterID'),
    url(r'^edit/stockTransferMasterID/(?P<pk>.*)/$',
        views.edit_stockTransferMasterID, name='edit_stockTransferMasterID'),
    url(r'^delete/stockTransferMasterID/(?P<pk>.*)/$',
        views.delete_stockTransferMasterID, name='delete_stockTransferMasterID'),
]
