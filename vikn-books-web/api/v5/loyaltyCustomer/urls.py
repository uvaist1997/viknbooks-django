from django.conf.urls import url, include
from api.v5.loyaltyCustomer import views


urlpatterns = [
    url(r'^create-loyaltyCustomer/$', views.create_loyaltyCustomer,
        name='create_loyaltyCustomer'),
    url(r'^loyaltyCustomers/$', views.loyaltyCustomers, name='loyaltyCustomers'),
    url(r'^view/loyaltyCustomer/(?P<pk>.*)/$',
        views.loyaltyCustomer, name='loyaltyCustomer'),
    url(r'^edit/loyaltyCustomer/(?P<pk>.*)/$',
        views.edit_loyaltyCustomer, name='edit_loyaltyCustomer'),
    url(r'^delete/loyaltyCustomer/(?P<pk>.*)/$',
        views.delete_loyaltyCustomer, name='delete_loyaltyCustomer'),

    url(r'^card-types/$', views.card_types, name='card_types'),
    url(r'^card-status/$', views.card_status, name='card_status'),
    url(r'^sundry-debtors/$', views.sundry_debtors, name='sundry_debtors'),
    url(r'^get-cardNumber-detail/$', views.get_cardNumber_detail,
        name='get_cardNumber_detail'),
    url(r'^get-mobileNo-detail/$', views.get_mobileNo_detail,
        name='get_mobileNo_detail'),
]
