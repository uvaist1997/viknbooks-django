from django.conf.urls import url,include
from api.v1.products import views


urlpatterns = [
	url(r'^create-product/$', views.create_product, name='create_product'),
    url(r'^products/$', views.products, name='products'),
    url(r'^view/product/(?P<pk>.*)/$', views.product, name='product'),
    url(r'^edit/product/(?P<pk>.*)/$', views.edit_product, name='edit_product'),
    url(r'^delete/product/(?P<pk>.*)/$', views.delete_product, name='delete_product'),
	url(r'^upload-product/$', views.upload_product, name='upload_product'),

	url(r'^products-test/$', views.products_test, name='products_test'),
	url(r'^products-search/$', views.products_search, name='products_search'),

	url(r'^get-product/barcode/$', views.get_product_barcode, name='get_product_barcode'),

	url(r'^list-products/under-groups/$', views.list_productsUnderGroups, name='list_productsUnderGroups'),
	url(r'^list-products/byBarcode/$', views.list_productsbyBarcode, name='list_productsbyBarcode'),
]