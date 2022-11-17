from django.conf.urls import url, include
from api.v4.salesReturnDetails import views


urlpatterns = [
    url(r'^create-salesReturnDetails/$', views.create_salesReturnDetails,
        name='create_salesReturnDetails'),
    url(r'^list/salesReturnDetails/$', views.list_salesReturnDetails,
        name='list_salesReturnDetails'),
    url(r'^view/salesReturnDetails/(?P<pk>.*)/$',
        views.salesReturnDetails, name='salesReturnDetails'),
    url(r'^edit/salesReturnDetails/(?P<pk>.*)/$',
        views.edit_salesReturnDetails, name='edit_salesReturnDetails'),
    url(r'^delete/salesReturnDetails/(?P<pk>.*)/$',
        views.delete_salesReturnDetails, name='delete_salesReturnDetails'),

    url(r'^create-salesReturnDetailsDummy/$',
        views.create_salesReturnDetailsDummy, name='create_salesReturnDetailsDummy'),
    url(r'^list/salesReturnDetailsDummy/$',
        views.list_salesReturnDetailsDummy, name='list_salesReturnDetailsDummy'),
    url(r'^edit/salesReturnDetailsDummy/(?P<pk>.*)/$',
        views.edit_salesReturnDetailsDummy, name='edit_salesReturnDetailsDummy'),
    url(r'^delete/salesReturnDetailsDummy/(?P<pk>.*)/$',
        views.delete_salesReturnDetailsDummy, name='delete_salesReturnDetailsDummy'),

    url(r'^create-DummyforEditSalesReturn/$',
        views.create_DummyforEditSalesReturn, name='create_DummyforEditSalesReturn'),
]
