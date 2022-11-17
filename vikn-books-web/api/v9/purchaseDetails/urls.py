from django.conf.urls import url, include
from api.v9.purchaseDetails import views


urlpatterns = [
    url(r'^create-purchaseDetails/$', views.create_purchaseDetails,
        name='create_purchaseDetails'),
    url(r'^list/purchaseDetails/$', views.list_purchaseDetails,
        name='list_purchaseDetails'),
    url(r'^view/purchaseDetail/(?P<pk>.*)/$',
        views.purchaseDetail, name='purchaseDetail'),
    url(r'^edit/purchaseDetails/(?P<pk>.*)/$',
        views.edit_purchaseDetails, name='edit_purchaseDetails'),
    url(r'^delete/purchaseDetails/(?P<pk>.*)/$',
        views.delete_purchaseDetails, name='delete_purchaseDetails'),

    url(r'^create-purchasesDetailsDummy/$',
        views.create_purchasesDetailsDummy, name='create_purchasesDetailsDummy'),
    url(r'^list/purchasesDetailsDummy/$', views.list_purchasesDetailsDummy,
        name='list_purchasesDetailsDummy'),
    url(r'^edit/purchasesDetailsDummy/(?P<pk>.*)/$',
        views.edit_purchasesDetailsDummy, name='edit_purchasesDetailsDummy'),
    url(r'^delete/purchasesDetailsDummy/(?P<pk>.*)/$',
        views.delete_purchasesDetailsDummy, name='delete_purchasesDetailsDummy'),

    url(r'^create-DummyforEditPurchase/$',
        views.create_DummyforEditPurchase, name='create_DummyforEditPurchase'),
]
