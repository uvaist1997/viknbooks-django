from django.conf.urls import url, include
from api.v9.products import views


urlpatterns = [
    url(r'^check-barcode/$', views.check_barcode, name='check_barcode'),
    url(r'^create-product/$', views.create_product, name='create_product'),
    url(r'^products/$', views.products, name='products'),
    url(r'^view/product/(?P<pk>.*)/$', views.product, name='product'),
    url(r'^edit/product/(?P<pk>.*)/$', views.edit_product, name='edit_product'),
    url(r'^delete/product/(?P<pk>.*)/$',
        views.delete_product, name='delete_product'),
    url(r'^upload-product/$', views.upload_product, name='upload_product'),
    url(r'^get-progress/(?P<task_id>[\w-]+)/$',
        views.get_progress, name='task_status'),

    url(r'^products-test/$', views.products_test, name='products_test'),
    url(r'^products-test-invoice/$', views.products_test_invoice,
        name='products_test_invoice'),
    url(r'^products-search/$', views.products_search, name='products_search'),
    url(r'^products-search-web/$', views.products_search_web,
        name='products_search_web'),
    url(r'^products-search-invoice/$', views.products_search_invoice,
        name='products_search_invoice'),
    url(r'^products-search-shortcut/$', views.products_search_shortcut,
        name='products_search_shortcut'),
    url(r'^products-search-shortcut-barcode/$',
        views.products_search_shortcut_barcode, name='products_search_shortcut_barcode'),

    url(r'^get-product/barcode/$', views.get_product_barcode,
        name='get_product_barcode'),

    # create product
    url(r'^get-single-product/barcode/$', views.get_single_product_barcode,
        name='get_single_product_barcode'),
    #########
    url(r'^products-search-batch/$', views.products_search_batch,
        name='products_search_batch'),

    url(r'^list-products/under-groups/$',
        views.list_productsUnderGroups, name='list_productsUnderGroups'),
    url(r'^list-products/byBarcode/$', views.list_productsbyBarcode,
        name='list_productsbyBarcode'),
    url(r'^products-update/$', views.products_update, name='products_update'),
    url(r'^product-analysis-report/$', views.product_analysis_report,
        name='product_analysis_report'),

    url(r'^set-product-tax/$', views.set_product_tax, name='set_product_tax'),
    url(r'^search-product-list/$', views.search_product_list,
        name='search_product_list'),

    url(r'^get-product/batchcode/$', views.get_product_batchcode,
        name='get_product_batchcode'),

    url(r'^get-batch/list/$', views.get_batch_list,
        name='get_batch_list'),

    url(r'^batch/report/$', views.batch_report,
        name='batch_report'),

    url(r'^products-export-excel$', views.products_export_excel,
        name='products_export_excel'),

    url(r'^productCode-search/$', views.productCode_search,
        name='productCode_search'),
    url(r'^products-search-qry/$', views.products_search_qry,
        name='products_search_qry'),
    
    url(r'^products-search-app/$', views.products_search_app,
        name='products_search_app'),
    
    url(r'^get-product-details/$', views.get_product_details,
        name='get_product_details'),
    
]
