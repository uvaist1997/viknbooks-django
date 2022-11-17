from django.conf.urls import url, include
from api.v10.stockReceipts import views


urlpatterns = [
    url(r'^create-stockReceipt/$', views.create_stockReceipt,
        name='create_stockReceipt'),
    url(r'^edit/stockReceipt/(?P<pk>.*)/$',
        views.edit_stockReceipt, name='edit_stockReceipt'),
    url(r'^list/stockReceiptMasterID/$', views.list_stockReceiptMasterID,
        name='list_stockReceiptMasterID'),
    url(r'^view/stockReceiptMasterID/(?P<pk>.*)/$',
        views.stockReceiptMasterID, name='stockReceiptMasterID'),
    url(r'^delete/stockReceiptDetails/(?P<pk>.*)/$',
        views.delete_stockReceiptDetails, name='delete_stockReceiptDetails'),
    url(r'^delete/stockReceiptMasterID/(?P<pk>.*)/$',
        views.delete_stockReceiptMasterID, name='delete_stockReceiptMasterID'),
]
