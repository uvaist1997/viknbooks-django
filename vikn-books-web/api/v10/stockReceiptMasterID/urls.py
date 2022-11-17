from django.conf.urls import url, include
from api.v10.stockReceiptMasterID import views


urlpatterns = [
    url(r'^create-stockReceiptMasterID/$',
        views.create_stockReceiptMasterID, name='create_stockReceiptMasterID'),
    url(r'^list/stockReceiptMasterID/$', views.list_stockReceiptMasterID,
        name='list_stockReceiptMasterID'),
    url(r'^view/stockReceiptMasterID/(?P<pk>.*)/$',
        views.stockReceiptMasterID, name='stockReceiptMasterID'),
    url(r'^edit/stockReceiptMasterID/(?P<pk>.*)/$',
        views.edit_stockReceiptMasterID, name='edit_stockReceiptMasterID'),
    url(r'^delete/stockReceiptMasterID/(?P<pk>.*)/$',
        views.delete_stockReceiptMasterID, name='delete_stockReceiptMasterID'),
]
