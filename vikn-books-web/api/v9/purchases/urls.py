from django.conf.urls import url, include
from api.v9.purchases import views


urlpatterns = [
    url(r'^create-purchase/$', views.create_purchase, name='create_purchase'),
    url(r'^edit/purchase/(?P<pk>.*)/$', views.edit_purchase, name='edit_purchase'),
    url(r'^list/purchaseMaster/$', views.list_purchaseMaster,
        name='list_purchaseMaster'),
    url(r'^purchase-pagination/$', views.purchase_pagination,
        name='purchase_pagination'),
    url(r'^view/purchaseMaster/(?P<pk>.*)/$',
        views.purchaseMaster, name='purchaseMaster'),
    # url(r'^delete/purchaseDetails/(?P<pk>.*)/$', views.delete_purchaseDetails, name='delete_purchaseDetails'),
    url(r'^delete/purchaseMaster/(?P<pk>.*)/$',
        views.delete_purchaseMaster, name='delete_purchaseMaster'),

    url(r'^purchaseInvoice-for-purchaseReturn/$',
        views.purchaseInvoice_for_PurchaseReturn, name='purchaseInvoice_for_PurchaseReturn'),

    url(r'^purchases/mobile/report/$', views.purchases_mobile_report,
        name='purchases_mobile_report'),
    url(r'^report/purchases/$', views.report_purchases, name='report_purchases'),
    url(r'^report/purchase-return/$', views.report_purchase_return,
        name='report_purchase_return'),

    url(r'^default-values/$', views.default_values, name='default_values'),

    url(r'^search-purchases/$', views.search_purchases, name='search_purchases'),

    url(r'^purchaseOrder-for-purchaseInvoice/$',
        views.purchaseOrder_for_purchaseInvoice, name='purchaseOrder_for_salesInvoice'),

    url(r'^purchase-register/report/$', views.purchaseRegister_report,
        name='purchaseRegister_report'),

    url(r'^gst-purchase-report/$',
        views.gst_purchase_report, name='gst_purchase_report'),

    url(r'^purchase/gstR-report/$',
        views.purchase_gstr_report, name='purchase_gstr_report'),

    url(r'^purchase-taxgroup-report-excel/$',
        views.purchase_taxgroup_report_excel, name='purchase_taxgroup_report_excel'),
    url(r'^purchase-gst-report-excel/$', views.purchase_gst_report_excel,
        name='purchase_gst_report_excel'),

    url(r'^search-purchase-list/$', views.search_purchase_list,
        name='search_purchase_list'),

    url(r'^purchase-report-excel/$', views.purchase_report_excel,
        name='purchase_report_excel'),
    
    url(r'^purchase-register/report-qry/$', views.purchaseRegister_report_qry,
        name='purchaseRegister_report_qry'),
    url(r'^purchase/integrated-report/$',
        views.purchase_integrated_report, name='purchase_integrated_report'),
    url(r'^get-orderDetails/$', views.get_order_details, name='get_order_details'),
    url(r'^filterd-purchaseOreders/$', views.purchase_filterd_purchase_order,
        name='purchase_filterd_purchase_order'),
]
