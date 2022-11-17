from django.conf.urls import url,include
from api.v1.stockReceiptDetails import views


urlpatterns = [
	url(r'^create-stockReceiptDetails/$', views.create_stockReceiptDetails, name='create_stockReceiptDetails'),
    url(r'^list/stockReceiptDetails/$', views.list_stockReceiptDetails, name='list_stockReceiptDetails'),
    url(r'^view/receiptDetail/(?P<pk>.*)/$', views.receiptDetail, name='receiptDetail'),
    url(r'^edit/stockReceiptDetails/(?P<pk>.*)/$', views.edit_stockReceiptDetails, name='edit_stockReceiptDetails'),
    url(r'^delete/stockReceiptDetails/(?P<pk>.*)/$', views.delete_stockReceiptDetails, name='delete_stockReceiptDetails'),

    url(r'^create-stockReceiptDetailsDummy/$', views.create_stockReceiptDetailsDummy, name='create_stockReceiptDetailsDummy'),
    url(r'^list/stockReceiptDetailsDummy/$', views.list_stockReceiptDetailsDummy, name='list_stockReceiptDetailsDummy'),
    url(r'^edit/stockReceiptDetailsDummy/(?P<pk>.*)/$', views.edit_stockReceiptDetailsDummy, name='edit_stockReceiptDetailsDummy'),
    url(r'^delete/stockReceiptDetailsDummy/(?P<pk>.*)/$', views.delete_stockReceiptDetailsDummy, name='delete_stockReceiptDetailsDummy'),

    url(r'^create-DummyforEditStockReceiptMaster/$', views.create_DummyforEditStockReceiptMaster, name='create_DummyforEditStockReceiptMaster'),
]