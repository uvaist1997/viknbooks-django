from django.conf.urls import url, include
from api.v7.receiptDetails import views


urlpatterns = [
    url(r'^create-receiptDetails/$', views.create_receiptDetails,
        name='create_receiptDetails'),
    url(r'^list/receiptDetails/$', views.list_receiptDetails,
        name='list_receiptDetails'),
    url(r'^view/receiptDetail/(?P<pk>.*)/$',
        views.receiptDetail, name='receiptDetail'),
    url(r'^edit/receiptDetails/(?P<pk>.*)/$',
        views.edit_receiptDetails, name='edit_receiptDetails'),
    url(r'^delete/receiptDetails/(?P<pk>.*)/$',
        views.delete_receiptDetails, name='delete_receiptDetails'),

    url(r'^create-receiptDetailsDummy/$', views.create_receiptDetailsDummy,
        name='create_receiptDetailsDummy'),
    url(r'^list/receiptDetailsDummy/$', views.list_receiptDetailsDummy,
        name='list_receiptDetailsDummy'),
    url(r'^edit/receiptDetailsDummy/(?P<pk>.*)/$',
        views.edit_receiptDetailsDummy, name='edit_receiptDetailsDummy'),
    url(r'^delete/receiptDetailsDummy/(?P<pk>.*)/$',
        views.delete_receiptDetailsDummy, name='delete_receiptDetailsDummy'),

    url(r'^create-DummyforEditReceiptMaster/$',
        views.create_DummyforEditReceiptMaster, name='create_DummyforEditReceiptMaster'),
]
