from django.conf.urls import url, include
from api.v8.pos_apis import views


urlpatterns = [
    url(r'^pos-companies/$', views.pos_companies, name='pos_companies'),
    url(r'^pos-product-list/$', views.pos_product_list, name='pos_product_list'),
    url(r'^pos-parties/$', views.pos_parties, name='pos_parties'),
    url(r'^pos-device-registration/$', views.pos_device_registration,
        name='pos_device_registration'),
    url(r'^pos-device-data/$', views.pos_device_data, name='pos_device_data'),

    url(r'^pos-get-sales/$', views.pos_get_sales, name='pos_get_sales'),
    url(r'^pos-get-product-barcode/$', views.pos_get_product_barcode,
        name='pos_get_product_barcode'),

    url(r'^pos-create/sale/$', views.pos_create_sale, name='pos_create_sale'),
    url(r'^pos-create/sale-return/$', views.pos_create_sale_return,
        name='pos_create_sale_return'),

    url(r'^pos-get-device-data/id/$',
        views.pos_get_device_data, name='pos_get_device_data'),

    url(r'^pos-branch-list/$', views.pos_branch_list, name='pos_branch_list'),
]
