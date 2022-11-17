from django.conf.urls import url, include
from api.v5.receipts import views


urlpatterns = [
    url(r'^create-receipt/$', views.create_receipt, name='create_receipt'),
    url(r'^edit/receipt/(?P<pk>.*)/$', views.edit_receipt, name='edit_receipt'),
    url(r'^list/receiptMaster/$', views.list_receiptMaster,
        name='list_receiptMaster'),
    url(r'^view/receiptMaster/(?P<pk>.*)/$',
        views.receiptMaster, name='receiptMaster'),
    # url(r'^delete/receiptDetails/(?P<pk>.*)/$', views.delete_receiptDetails, name='delete_receiptDetails'),
    url(r'^delete/receiptMaster/(?P<pk>.*)/$',
        views.delete_receiptMaster, name='delete_receiptMaster'),

    url(r'^search-receipts/$', views.search_receipts, name='search_receipts'),
    url(r'^report-receipts/$', views.report_receipts, name='report_receipts'),
]
