from django.conf.urls import url, include
from api.v5.purchaseReturnDetails import views


urlpatterns = [
    url(r'^create-purchaseReturnDetails/$',
        views.create_purchaseReturnDetails, name='create_purchaseReturnDetails'),
    url(r'^list/purchaseReturnDetails/$', views.list_purchaseReturnDetails,
        name='list_purchaseReturnDetails'),
    url(r'^view/purchaseReturnDetails/(?P<pk>.*)/$',
        views.purchaseReturnDetails, name='purchaseReturnDetails'),
    url(r'^edit/purchaseReturnDetails/(?P<pk>.*)/$',
        views.edit_purchaseReturnDetails, name='edit_purchaseReturnDetails'),
    url(r'^delete/purchaseReturnDetails/(?P<pk>.*)/$',
        views.delete_purchaseReturnDetails, name='delete_purchaseReturnDetails'),

    url(r'^create-purchasesReturnDetailsDummy/$',
        views.create_purchasesReturnDetailsDummy, name='create_purchasesReturnDetailsDummy'),
    url(r'^list/purchasesReturnDetailsDummy/$',
        views.list_purchasesReturnDetailsDummy, name='list_purchasesReturnDetailsDummy'),
    url(r'^edit/purchasesReturnDetailsDummy/(?P<pk>.*)/$',
        views.edit_purchasesReturnDetailsDummy, name='edit_purchasesReturnDetailsDummy'),
    url(r'^delete/purchasesReturnDetailsDummy/(?P<pk>.*)/$',
        views.delete_purchasesReturnDetailsDummy, name='delete_purchasesReturnDetailsDummy'),

    url(r'^create-DummyforEditPurchaseReturn/$',
        views.create_DummyforEditPurchaseReturn, name='create_DummyforEditPurchaseReturn'),
]
