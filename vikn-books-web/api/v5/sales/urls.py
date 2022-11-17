from django.conf.urls import url, include
from api.v5.sales import views


urlpatterns = [
    url(r'^create-sale/$', views.create_sale, name='create_sale'),
    url(r'^edit/sales/(?P<pk>.*)/$', views.edit_sales, name='edit_sales'),
    url(r'^list/salesMaster/$', views.list_salesMaster, name='list_salesMaster'),
    url(r'^sale-pagination/$', views.sale_pagination, name='sale_pagination'),
    url(r'^view/salesMaster/(?P<pk>.*)/$',
        views.salesMaster, name='salesMaster'),
    # url(r'^delete/salesDetails/(?P<pk>.*)/$', views.delete_salesDetails, name='delete_salesDetails'),
    url(r'^delete/salesMaster/(?P<pk>.*)/$',
        views.delete_salesMaster, name='delete_salesMaster'),

    url(r'^salesInvoice-for-salesReturn/$',
        views.salesInvoice_for_SalesReturn, name='salesInvoice_for_SalesReturn'),

    url(r'^salesInvoice-for-salesEstimate/$',
        views.salesInvoice_for_SalesEstimate, name='salesInvoice_for_SalesEstimate'),

    url(r'^sales/gst-sale-report/$',
        views.gst_sales_report, name='gst_sales_report'),

    url(r'^sales/report/$', views.sales_report, name='sales_report'),
    url(r'^searchLedger/sales/report/$', views.searchLedger_sales_report, name='searchLedger_sales_report'),
    url(r'^sales/integrated-report/$',
        views.sales_integrated_report, name='sales_report'),
    url(r'^vat/report/$', views.vat_report, name='vat_report'),
    url(r'^stock/report/$', views.stock_report, name='stock_report'),
    url(r'^stock-ledger/report/$', views.stock_ledger_report,
        name='stock_ledger_report'),
    url(r'^stock/report/print/$', views.stock_report_print,
        name='stock_report_print'),
    url(r'^stock-value/report/$', views.stockValue_report, name='stockValue_report'),
    url(r'^stock-value/report/print/$', views.stockValue_report_print,
        name='stockValue_report_print'),
    url(r'^sales-register/report/$', views.salesRegister_report,
        name='salesRegister_report'),
    url(r'^bill-wise/report/$', views.billWise_report, name='billWise_report'),

    url(r'^excess-stock/report/$', views.excessStock_report,
        name='excessStock_report'),
    url(r'^shortage-stock/report/$', views.shortageStock_report,
        name='shortageStock_report'),
    url(r'^damage-stock/report/$', views.damageStock_report,
        name='damageStock_report'),
    url(r'^used-stock/report/$', views.usedStock_report, name='usedStock_report'),

    url(r'^generate/voucherNo/$', views.generateVoucherNo, name='generateVoucherNo'),
    url(r'^generate/print-report/$', views.generate_printReport,
        name='generate_printReport'),

    url(r'^batch-wise/report/$', views.batchwise_report, name='batchwise_report'),
    url(r'^sales-summary/report/$', views.sales_summary_report,
        name='sales_summary_report'),
    url(r'^supplierVsproduct/report/$', views.supplier_vs_product_report,
        name='supplier_vs_product_report'),

    url(r'^salesOrder-for-salesInvoice/$',
        views.salesOrder_for_salesInvoice, name='salesOrder_for_salesInvoice'),

    url(r'^search-sales/$', views.search_sales, name='search_sales'),
    url(r'^product/report/$', views.product_report, name='product_report'),

    url(r'^inventory-flow/report/$', views.inventory_flow_report,
        name='inventory_flow_report'),

    url(r'^sales/grand-totals/$', views.sales_grand_totals,
        name='sales_grand_totals'),
    url(r'^filterd-salesOreders/$', views.sales_filterd_sales_order,
        name='sales_filterd_sales_order'),
    url(r'^get-orderDetails/$', views.get_order_details, name='get_order_details'),
]
