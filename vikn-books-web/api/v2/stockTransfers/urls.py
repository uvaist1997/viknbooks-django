from django.conf.urls import url,include
from api.v2.stockTransfers import views


urlpatterns = [
	url(r'^create-stockTransfer/$', views.create_stockTransfer, name='create_stockTransfer'),
    url(r'^edit/stockTransfer/(?P<pk>.*)/$', views.edit_stockTransfer, name='edit_stockTransfer'),
    url(r'^list/stockTransferMaster/$', views.list_stockTransferMasterID, name='list_stockTransferMasterID'),
    url(r'^stock-transfer-pagination/$', views.stock_transfer_pagination, name='stock_transfer_pagination'),
    url(r'^view/stockTransferMaster/(?P<pk>.*)/$', views.stockTransferMasterID, name='stockTransferMasterID'),
    url(r'^delete/stockTransferDetail/(?P<pk>.*)/$', views.delete_stockTransferDetails, name='delete_stockTransferDetails'),
    url(r'^delete/stockTransferMaster/(?P<pk>.*)/$', views.delete_stockTransferMasterID, name='delete_stockTransferMasterID'),
]