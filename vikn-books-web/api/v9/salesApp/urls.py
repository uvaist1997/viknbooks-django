from django.conf.urls import url, include
from api.v9.salesApp import views


urlpatterns = [
    url(r'^salesApp-companies/$', views.salesApp_companies,
        name='salesApp_companies'),
    url(r'^pos-product-list/$', views.pos_product_list, name='pos_product_list'),
    url(r'^pos-product-search/$', views.pos_product_search,
        name='pos_product_search'),
    url(r'^pos-parties/$', views.pos_parties, name='pos_parties'),
    url(r'^salesApp-login/$', views.salesApp_login, name='salesApp_login'),
    url(r'^pos-product-barcode/$', views.pos_product_barcode,
        name='pos_product_barcode'),
    
    url(r'^salesApp-create/sale/$', views.salesApp_create_sale,
        name='salesApp_create_sale'),
    url(r'^salesApp-edit/sales/(?P<pk>.*)/$',
        views.salesApp_edit_sales, name='salesApp_edit_sales'),
    url(r'^list-sales/$', views.list_sales, name='list_sales'),
    url(r'^salesApp-view/salesMaster/(?P<pk>.*)/$',
        views.salesApp_salesMaster, name='salesApp_salesMaster'),
    url(r'^salesApp-delete/salesMaster/(?P<pk>.*)/$',
        views.salesApp_delete_salesMaster, name='salesApp_delete_salesMaster'),
    
    url(r"^salesApp-create-salesReturn/$", views.salesApp_create_salesReturn,
        name="salesApp_create_salesReturn"),
    url(
        r"^salesApp-edit/salesReturn/(?P<pk>.*)/$",
        views.salesApp_edit_salesReturn,
        name="salesApp_edit_salesReturn",
    ),
    url(
        r"^salesApp-view/salesReturnMaster/(?P<pk>.*)/$",
        views.salesApp_salesReturnMaster,
        name="salesApp_salesReturnMaster",
    ),
    url(
        r"^salesApp-delete/salesReturnMaster/(?P<pk>.*)/$",
        views.salesApp_delete_salesReturnMaster,
        name="salesApp_delete_salesReturnMaster",
    ),
    url(r'^list-sales/return/$', views.list_sales_return, name='list_sales_return'),
    
    url(r'^list-sales/order/$', views.list_sales_order, name='list_sales_order'),
    url(r'^salesApp-create-salesOrder/$', views.salesApp_create_salesOrder, name='salesApp_create_salesOrder'),
    url(r'^salesApp-edit/salesOrder/(?P<pk>.*)/$',
        views.salesApp_edit_salesOrder, name='salesApp_edit_salesOrder'),
    url(r'^salesApp-view/salesOrderMaster/(?P<pk>.*)/$',
        views.salesApp_salesOrderMaster, name='salesApp_salesOrderMaster'),
    url(r'^salesApp-delete/salesOrderMaster/(?P<pk>.*)/$',
        views.salesApp_delete_salesOrderMaster, name='salesApp_delete_salesOrderMaster'),
    
    url(r'^list-payment/$', views.list_payment, name='list_payment'),
    url(r'^create-payment/$', views.create_payment, name='create_payment'),
    url(r'^salesApp-view/payment/(?P<pk>.*)/$',
        views.salesApp_payment, name='salesApp_payment'),
    url(r'^salesApp-edit/payment/(?P<pk>.*)/$',
        views.salesApp_edit_payment, name='salesApp_edit_payment'),
    url(r'^salesApp-delete/payment/(?P<pk>.*)/$',
        views.salesApp_delete_payment, name='salesApp_delete_payment'),
    
    url(r'^list-receipt/$', views.list_receipt, name='list_receipt'),
    url(r'^create-receipt/$', views.create_receipt, name='create_receipt'),
    url(r'^salesApp-view/receipt/(?P<pk>.*)/$',
        views.salesApp_receipt, name='salesApp_receipt'),
    url(r'^salesApp-edit/receipt/(?P<pk>.*)/$',
        views.salesApp_edit_receipt, name='salesApp_edit_receipt'),
    url(r'^salesApp-delete/receipt/(?P<pk>.*)/$',
        views.salesApp_delete_receipt, name='salesApp_delete_receipt'),
    
    url(r'^list-salesApp/expense/$', views.list_salesApp_expense,
        name='list_salesApp_expense'),
    url(r'^salesApp-create-expense/$', views.salesApp_create_expense, name='salesApp_create_expense'),
    url(r'^salesApp-edit/expense/(?P<pk>.*)/$', views.salesApp_edit_expense, name='salesApp_edit_expense'),
    url(r'^salesApp-view/expense/(?P<pk>.*)/$', views.salesApp_expense, name='salesApp_expense'),
    url(r'^salesApp-delete/expense/(?P<pk>.*)/$',
        views.salesApp_delete_expense, name='salesApp_delete_expense'),
    
    url(r'^list-stock/order/$', views.list_stock_order, name='list_stock_order'),
    url(r'^salesApp-create-stockOrder/$', views.salesApp_create_stockOrder,
        name='salesApp_create_stockOrder'),
    url(r'^salesApp-edit/stockOrder/(?P<pk>.*)/$',
        views.salesApp_edit_stockOrder, name='salesApp_edit_stockOrder'),
    url(r'^salesApp-view/stockOrderMaster/(?P<pk>.*)/$',
        views.salesApp_stockOrderMasterID, name='salesApp_stockOrderMasterID'),
    url(r'^salesApp-delete/stockOrderMaster/(?P<pk>.*)/$',
        views.salesApp_delete_stockOrderMasterID, name='salesApp_delete_stockOrderMasterID'),
    
    url(r'^list-stock/transfer/$', views.list_stock_transfer, name='list_stock_transfer'),
    url(
        r"^salesApp-create-stockTransfer/$",
        views.salesApp_create_stockTransfer,
        name="salesApp_create_stockTransfer",
    ),
    url(
        r"^salesApp-edit/stockTransfer/(?P<pk>.*)/$",
        views.salesApp_edit_stockTransfer,
        name="salesApp_edit_stockTransfer",
    ),
    url(
        r"^salesApp-view/stockTransferMaster/(?P<pk>.*)/$",
        views.salesApp_stockTransferMasterID,
        name="salesApp_stockTransferMasterID",
    ),
    url(
        r"^salesApp-delete/stockTransferMaster/(?P<pk>.*)/$",
        views.salesApp_delete_stockTransferMasterID,
        name="salesApp_delete_stockTransferMasterID",
    ),
    url(r'^salesApp/summary/$', views.salesApp_summary,
        name='salesApp_summary'),
    
    url(r'^salesApp/dashboard/$', views.salesApp_dashboard,
        name='salesApp_dashboard'),
    
]
