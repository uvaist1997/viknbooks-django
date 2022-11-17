from django.conf.urls import url, include
from api.v6.workOrder import views


urlpatterns = [
    url(r'^create-workorder/$', views.create_workorder, name='create_workorder'),
    url(r'^edit-workorder/(?P<pk>.*)/$',
        views.edit_workorder, name='edit_workorder'),
    url(r'^workorders/$', views.workorders, name='workorders'),
    url(r'^workorders-scroll/$', views.workorders_scroll, name='workorders_scroll'),
    url(r'^workorders-search/$', views.workorders_search, name='workorders_search'),
    url(r'^workorder/(?P<pk>.*)/$', views.workorder, name='workorder'),
    url(r'^delete/workorder/(?P<pk>.*)/$',
        views.delete_workorder, name='delete_workorder'),
    #   	url(r'^purchase-pagination/$', views.purchase_pagination, name='purchase_pagination'),
    #    url(r'^view/purchaseMaster/(?P<pk>.*)/$', views.purchaseMaster, name='purchaseMaster'),
    #    # url(r'^delete/purchaseDetails/(?P<pk>.*)/$', views.delete_purchaseDetails, name='delete_purchaseDetails'),
    #    url(r'^delete/purchaseMaster/(?P<pk>.*)/$', views.delete_purchaseMaster, name='delete_purchaseMaster'),

    #    url(r'^purchaseInvoice-for-purchaseReturn/$', views.purchaseInvoice_for_PurchaseReturn, name='purchaseInvoice_for_PurchaseReturn'),

    #    url(r'^report/purchases/$', views.report_purchases, name='report_purchases'),

    #    url(r'^default-values/$', views.default_values, name='default_values'),
]
