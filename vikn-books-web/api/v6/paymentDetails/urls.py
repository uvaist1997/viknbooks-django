from django.conf.urls import url, include
from api.v6.paymentDetails import views


urlpatterns = [
    url(r'^create-paymentDetails/$', views.create_paymentDetails,
        name='create_paymentDetails'),
    url(r'^list/paymentDetails/$', views.list_paymentDetails,
        name='list_paymentDetails'),
    url(r'^view/paymentDetails/(?P<pk>.*)/$',
        views.paymentDetails, name='paymentDetails'),
    url(r'^edit/paymentDetails/(?P<pk>.*)/$',
        views.edit_paymentDetails, name='edit_paymentDetails'),
    url(r'^delete/paymentDetails/(?P<pk>.*)/$',
        views.delete_paymentDetails, name='delete_paymentDetails'),

    url(r'^create-paymentDetailsDummy/$', views.create_paymentDetailsDummy,
        name='create_paymentDetailsDummy'),
    url(r'^list/paymentDetailsDummy/$', views.list_paymentDetailsDummy,
        name='list_paymentDetailsDummy'),
    url(r'^edit/paymentDetailsDummy/(?P<pk>.*)/$',
        views.edit_paymentDetailsDummy, name='edit_paymentDetailsDummy'),
    url(r'^delete/paymentDetailsDummy/(?P<pk>.*)/$',
        views.delete_paymentDetailsDummy, name='delete_paymentDetailsDummy'),

    url(r'^create-DummyforEditPaymentMaster/$',
        views.create_DummyforEditPaymentMaster, name='create_DummyforEditPaymentMaster'),
]
