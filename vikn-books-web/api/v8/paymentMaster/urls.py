from django.conf.urls import url, include
from api.v8.paymentMaster import views


urlpatterns = [
    url(r'^create-paymentMaster/$', views.create_paymentMaster,
        name='create_paymentMaster'),
    url(r'^list/paymentMasters/$', views.list_paymentMasters,
        name='list_paymentMasters'),
    url(r'^view/paymentMaster/(?P<pk>.*)/$',
        views.paymentMaster, name='paymentMaster'),
    url(r'^edit/paymentMaster/(?P<pk>.*)/$',
        views.edit_paymentMaster, name='edit_paymentMaster'),
    url(r'^delete/paymentMaster/(?P<pk>.*)/$',
        views.delete_paymentMaster, name='delete_paymentMaster'),
]
