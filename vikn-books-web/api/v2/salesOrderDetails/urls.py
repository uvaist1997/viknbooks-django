from django.conf.urls import url,include
from api.v2.salesOrderDetails import views


urlpatterns = [
	url(r'^create-salesOrderDetails/$', views.create_salesOrderDetails, name='create_salesOrderDetails'),
    url(r'^list/salesOrderDetails/$', views.list_salesOrderDetails, name='list_salesOrderDetails'),
    url(r'^view/salesOrderDetails/(?P<pk>.*)/$', views.salesOrderDetails, name='salesOrderDetails'),
    url(r'^edit/salesOrderDetails/(?P<pk>.*)/$', views.edit_salesOrderDetails, name='edit_salesOrderDetails'),
    url(r'^delete/salesOrderDetails/(?P<pk>.*)/$', views.delete_salesOrderDetails, name='delete_salesOrderDetails'),

    url(r'^create-salesOrderDetailsDummy/$', views.create_salesOrderDetailsDummy, name='create_salesOrderDetailsDummy'),
    url(r'^list/salesOrderDetailsDummy/$', views.list_salesOrderDetailsDummy, name='list_salesOrderDetailsDummy'),
    url(r'^edit/salesOrderDetailsDummy/(?P<pk>.*)/$', views.edit_salesOrderDetailsDummy, name='edit_salesOrderDetailsDummy'),
    url(r'^delete/salesOrderDetailsDummy/(?P<pk>.*)/$', views.delete_salesOrderDetailsDummy, name='delete_salesOrderDetailsDummy'),

    url(r'^create-DummyforEditSalesOrder/$', views.create_DummyforEditSalesOrder, name='create_DummyforEditSalesOrder'),
]