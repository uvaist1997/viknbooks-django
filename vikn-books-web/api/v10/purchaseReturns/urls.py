from django.conf.urls import url, include
from api.v10.purchaseReturns import views


urlpatterns = [
    url(r'^create-purchaseReturn/$', views.create_purchaseReturn,
        name='create_purchaseReturn'),
    url(r'^edit/purchaseReturn/(?P<pk>.*)/$',
        views.edit_purchaseReturn, name='edit_purchaseReturn'),
    url(r'^list/purchaseReturnMaster/$', views.list_purchaseReturnMaster,
        name='list_purchaseReturnMaster'),
    url(r'^purchase-return-pagination/$', views.purchase_return_pagination,
        name='purchase_return_pagination'),
    url(r'^view/purchaseReturnMaster/(?P<pk>.*)/$',
        views.purchaseReturnMaster, name='purchaseReturnMaster'),
    url(r'^delete/purchaseReturnMaster/(?P<pk>.*)/$',
        views.delete_purchaseReturnMaster, name='delete_purchaseReturnMaster'),
    url(r'^report/purchaseReturns/$', views.report_purchaseReturns,
        name='report_purchaseReturns'),

    url(r'^search-purchaseReturns/$', views.search_purchaseReturns,
        name='search_purchaseReturns'),

    url(r'^purchaseReturn-register/report/$', views.purchaseReturnRegister_report,
        name='purchaseReturnRegister_report'),

    url(r'^search-purchaseReturn-list/$', views.search_purchaseReturn_list, name='search_purchaseReturn_list'),
    url(r'^purchaseReturn-register/report-qry/$', views.purchaseReturnRegister_report_qry,
        name='purchaseReturnRegister_report_qry'),
]
