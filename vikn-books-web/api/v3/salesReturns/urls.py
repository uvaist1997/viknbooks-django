from django.conf.urls import url, include
from api.v3.salesReturns import views


urlpatterns = [
    url(r'^create-salesReturn/$', views.create_salesReturn,
        name='create_salesReturn'),
    url(r'^edit/salesReturn/(?P<pk>.*)/$',
        views.edit_salesReturn, name='edit_salesReturn'),
    url(r'^list/salesReturnMaster/$', views.list_salesReturnMaster,
        name='list_salesReturnMaster'),
    url(r'^sales-return-pagination/$', views.sales_return_pagination,
        name='sales_return_pagination'),
    url(r'^view/salesReturnMaster/(?P<pk>.*)/$',
        views.salesReturnMaster, name='salesReturnMaster'),
    url(r'^delete/salesReturnMaster/(?P<pk>.*)/$',
        views.delete_salesReturnMaster, name='delete_salesReturnMaster'),

    url(r'^report/salesReturns/$', views.report_salesReturns,
        name='report_salesReturns'),
]
