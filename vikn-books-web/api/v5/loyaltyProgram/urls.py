from django.conf.urls import url, include
from api.v5.loyaltyProgram import views


urlpatterns = [
    url(r'^create-loyaltyProgram/$', views.create_loyaltyProgram,
        name='create_loyaltyProgram'),
    url(r'^loyaltyPrograms/$', views.loyaltyPrograms, name='loyaltyPrograms'),
    url(r'^view/loyaltyProgram/(?P<pk>.*)/$',
        views.loyaltyProgram, name='loyaltyProgram'),
    url(r'^edit/loyaltyProgram/(?P<pk>.*)/$',
        views.edit_loyaltyProgram, name='edit_loyaltyProgram'),
    url(r'^delete/loyaltyProgram/(?P<pk>.*)/$',
        views.delete_loyaltyProgram, name='delete_loyaltyProgram'),

    url(r'^get_customer_point/(?P<pk>.*)/$',
        views.get_customer_point, name='get_customer_point'),

    url(r'^get-sigle-point/$', views.get_sigle_point, name='get_sigle_point'),
    url(r'^get-return-point/$', views.get_return_point, name='get_return_point'),
    url(r'^get-loyalty-customer/$', views.get_loyalty_customer,
        name='get_loyalty_customer'),
    url(r'^search-loyalty-customer/$', views.search_loyalty_customer,
        name='search_loyalty_customer'),


]
