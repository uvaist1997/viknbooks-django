from django.conf.urls import url, include
from api.v10.pos_apis import views


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

    url(r'^pos-version-insert/$', views.pos_version_insert,
        name='pos_version_insert'),

    url(r'^pos-version-check/$', views.pos_version_check,
        name='pos_version_check'),

    url(r'^pos-employees/$', views.pos_employees, name='pos_employees'),

    url(r'^pos-product-list-filter/$', views.pos_product_list_filter,
        name='pos_product_list_filter'),
    
    url(r'^faera-device-settings/$', views.faera_device_settings,
        name='faera_device_settings'),
    url(r'^faera-device-registration/$', views.faera_device_registration,
        name='faera_device_registration'),
    url(r'^get-faera-settings/$', views.get_faera_settings,
        name='get_faera_settings'),
    url(r'^faera/generate-device-code/$', views.faera_generate_device_code,
        name='faera_generate_device_code'),
    url(r"^faera-login/$", views.faera_login, name="faera_login"),
    
    url(r"^faera/sales-customer-list/$", views.faera_sale_customer_list, name="faera_sale_customer_list"),
    url(r"^faera-user/check/$", views.faera_user_check, name="faera_user_check"),
]
