from django.conf.urls import url, include
from api.v9.posholds import views


urlpatterns = [
    url(r'^create-poshold/$', views.create_poshold, name='create_poshold'),
    url(r'^edit/poshold/(?P<pk>.*)/$', views.edit_poshold, name='edit_poshold'),
    url(r'^list/posholdMaster/$', views.list_posholdMaster,
        name='list_posholdMaster'),
    url(r'^view/posholdMaster/(?P<pk>.*)/$',
        views.posholdMaster, name='posholdMaster'),
    url(r'^delete/posholdDetails/(?P<pk>.*)/$',
        views.delete_posholdDetails, name='delete_posholdDetails'),
    url(r'^delete/posholdMaster/(?P<pk>.*)/$',
        views.delete_posholdMaster, name='delete_posholdMaster'),

    url(r'^create-pos-role/$', views.create_pos_role, name='create_pos_role'),
    url(r'^create-pos-user/$', views.create_pos_user, name='create_pos_user'),
    url(r'^generate-pos-pin/$', views.generate_pos_pin, name='generate_pos_pin'),

    url(r'^list/pos-role/$', views.list_pos_role,
        name='list_pos_role'),
    url(r'^list/pos-users/$', views.list_pos_users,
        name='list_pos_users'),

    url(r'^delete/pos-role/(?P<pk>.*)/$',
        views.delete_pos_role, name='delete_pos_role'),

    url(r'^delete/pos-user/(?P<pk>.*)/$',
        views.delete_pos_user, name='delete_pos_user'),
    url(r'^single/pos-role/(?P<pk>.*)/$',
        views.single_pos_role, name='single_pos_role'),

    url(r'^single/pos-user/(?P<pk>.*)/$',
        views.single_pos_user, name='single_pos_user'),

    url(r'^edit/pos-role/(?P<pk>.*)/$',
        views.edit_pos_role, name='edit_pos_role'),

    url(r'^edit/pos-user/(?P<pk>.*)/$',
        views.edit_pos_user, name='edit_pos_user'),

    url(r'^validate-user-pin/$', views.validate_user_pin, name='validate_user_pin'),

    url(r'^pos-table-create/$', views.pos_table_create, name='pos_table_create'),
    url(r'^pos-table-list/$', views.pos_table_list, name='pos_table_list'),

    url(r'^pos/product-group/list/$', views.pos_product_group_list,
        name='pos_product_group_list'),
    url(r'^pos-product-list/$', views.pos_product_list, name='pos_product_list'),

    url(r'^create-pos/salesOrder/$', views.create_pos_salesOrder,
        name='create_pos_salesOrder'),
    url(r'^create-pos/salesInvoice/$', views.create_pos_salesInvoice,
        name='create_pos_salesInvoice'),
    url(r'^view-pos/salesOrder/(?P<pk>.*)/$',
        views.view_pos_salesOrder, name='view_pos_salesOrder'),

    url(r'^edit/pos-sales-order/(?P<pk>.*)/$',
        views.edit_pos_sales_order, name='edit_pos_sales_order'),

    url(r'^check-pos/table-delete/$', views.check_pos_table_delete,
        name='check_pos_table_delete'),
    url(r'^update-pos/settings/$', views.update_pos_settings,
        name='update_pos_settings'),

    url(r'^generate-pos-order/token-no/$',
        views.generate_pos_order_token_no, name='generate_pos_order_token_no'),
    url(r'^reset-status/$', views.reset_status, name='reset_status'),

    url(r'^list/order-reason/$', views.list_order_reason,
        name='list_order_reason'),
    url(r'^order-reason/$', views.order_reason,
        name='order_reason'),

    url(r'^products-search-pos/$', views.products_search_pos,
        name='products_search_pos'),

    url(r'^pos-companies/$', views.pos_companies, name='pos_companies'),

    url(r'^view/pos-sale/invoice/(?P<pk>.*)/$',
        views.pos_sale_invoice, name='pos_sale_invoice'),

    url(r'^pos-ledgerListByID/$', views.pos_ledgerListByID,
        name='pos_ledgerListByID'),

    url(r'^pos-kitchen/$', views.pos_kitchen,
        name='pos_kitchen'),
    
    url(r'^view/pos-kitchen/(?P<pk>.*)/$',
        views.view_pos_kitchen, name='view_pos_kitchen'),

    url(r'^list/pos-kitchen/$', views.list_pos_kitchen,
        name='list_pos_kitchen'),

    url(r'^kitchen-print/$', views.kitchen_print,
        name='kitchen_print'),

    url(r'^table-create/$', views.table_create,
        name='table_create'),
    url(r'^table-list/$', views.table_list,
        name='table_list'),

    url(r'^table-delete/$', views.table_delete,
        name='table_delete'),

    url(r'^get-default-values/$', views.get_defaults, name='get_defaults'),
    
    url(r'^customer-create/$', views.customer_create,
        name='customer_create'),
    url(r'^customer-list/$', views.customer_list,
        name='customer_list'),
    url(r'^single/customer/(?P<pk>.*)/$',
        views.single_customer, name='single_customer'),
    url(r'^delete/customer/(?P<pk>.*)/$',
        views.delete_customer, name='delete_customer'),
    url(r'^edit/customer/(?P<pk>.*)/$',
        views.edit_customer, name='edit_customer'),
    url(r'^printer-create/$', views.printer_create,
        name='printer_create'),
    url(r'^printer-list/$', views.printer_list,
        name='printer_list'),
    url(r'^delete/printer/(?P<pk>.*)/$',
        views.delete_printer, name='delete_printer'),
    url(r'^variant-create/$', views.variant_create,
        name='variant_create'),
    
    url(r'^variant-list/$', views.variant_list,
        name='variant_list'),
    
    url(r'^product-create/$', views.product_create,
        name='product_create'),
    url(r'^single/product/(?P<pk>.*)/$',
        views.single_product, name='single_product'),
    url(r'^edit/product/(?P<pk>.*)/$',
        views.edit_product, name='edit_product'),
    url(r'^delete/product/(?P<pk>.*)/$',
        views.delete_product, name='delete_product'),
    
    url(r'^create-pos-user-role/$', views.create_pos_user_role,
        name='create_pos_user_role'),
    url(r'^rassassy-reports/$', views.rassassy_reports,
        name='rassassy_reports'),
    
    url(r'^rassassy/create_loyality_customer/$', views.rassassy_create_loyality_customer,
        name='rassassy_create_loyality_customer'),
    url(r'^rassassy/list_loyality_customer/$', views.rassassy_list_loyality_customer,
        name='rassassy_list_loyality_customer'),
    url(r'^rassassy/search_loyality_customer/$', views.rassassy_search_loyality_customer,
        name='rassassy_search_loyality_customer'),
    url(r'^rassassy-view/loyaltyCustomer/(?P<pk>.*)/$',
        views.rassassy_loyaltyCustomer, name='rassassy_loyaltyCustomer'),
    
    url(r'^rassassy-edit/loyaltyCustomer/(?P<pk>.*)/$',
        views.rassassy_edit_loyaltyCustomer, name='rassassy_edit_loyaltyCustomer'),
    url(r'^rassassy-delete/loyaltyCustomer/(?P<pk>.*)/$',
        views.rassassy_delete_loyaltyCustomer, name='rassassy_delete_loyaltyCustomer'),
]
