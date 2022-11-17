from django.conf.urls import url, include
from api.v6.payments import views


urlpatterns = [
    url(r'^create-payment/$', views.create_payment, name='create_payment'),
    url(r'^edit/payment/(?P<pk>.*)/$', views.edit_payment, name='edit_payment'),
    url(r'^list/payments/$', views.list_paymentMasters, name='list_paymentMasters'),
    url(r'^view/paymentMaster/(?P<pk>.*)/$',
        views.paymentMaster, name='paymentMaster'),
    # url(r'^delete/paymentDetails/(?P<pk>.*)/$', views.delete_paymentDetails, name='delete_paymentDetails'),
    url(r'^delete/paymentMaster/(?P<pk>.*)/$',
        views.delete_paymentMaster, name='delete_paymentMaster'),

    url(r'^search-payments/$', views.search_payments, name='search_payments'),
    url(r'^report-payments/$', views.report_payments, name='report_payments'),
]
