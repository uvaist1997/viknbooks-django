from django.conf.urls import url, include
from api.v3.sales import views


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

    url(r'^sales/report/$', views.sales_report, name='sales_report'),
    url(r'^sales/integrated-report/$',
        views.sales_integrated_report, name='sales_report'),
    url(r'^vat/report/$', views.vat_report, name='vat_report'),
    url(r'^stock/report/$', views.stock_report, name='stock_report'),
    url(r'^stock-value/report/$', views.stockValue_report, name='stockValue_report'),
    url(r'^sales-register/report/$', views.salesRegister_report,
        name='salesRegister_report'),
    url(r'^bill-wise/report/$', views.billWise_report, name='billWise_report'),

    url(r'^excess-stock/report/$', views.excessStock_report,
        name='excessStock_report'),
    url(r'^damage-stock/report/$', views.damageStock_report,
        name='damageStock_report'),
    url(r'^used-stock/report/$', views.usedStock_report, name='usedStock_report'),

    url(r'^generate/voucherNo/$', views.generateVoucherNo, name='generateVoucherNo'),
    url(r'^generate/print-report/$', views.generate_printReport,
        name='generate_printReport'),

    url(r'^batch-wise/report/$', views.batchwise_report, name='batchwise_report'),
]
