from django.conf.urls import url, include
from api.v9.parties import views


urlpatterns = [
    url(r'^create-party/$', views.create_party, name='create_party'),
    url(r'^parties/$', views.parties, name='parties'),
    url(r'^view/party/(?P<pk>.*)/$', views.party, name='party'),
    url(r'^edit/party/(?P<pk>.*)/$', views.edit_party, name='edit_party'),
    url(r'^delete/party/(?P<pk>.*)/$', views.delete_party, name='delete_party'),
    url(r'^upload-party/$', views.upload_party, name='upload_party'),

    url(r'^search-parties/$', views.search_parties, name='search_parties'),

    url(r'^user-address/list/$', views.user_address_list, name='user_address_list'),
    url(r'^user-address/create/$', views.user_address_create,
        name='user_address_create'),
    url(r'^user-address/update/$', views.user_address_update,
        name='user_address_update'),

    url(r'^upload-parties/$', views.upload_parties, name='upload_parties'),
    url(r'^search/party-list/$', views.search_party_list, name='search_party_list'),
    
    url(r'^customer-summary/$', views.customer_summary, name='customer_summary'),
    url(r'^customer-summary/overview/$', views.customer_summary_overview,
        name='customer_summary_overview'),
    url(r'^customer-summary/overview-graph/$', views.customer_summary_overview_graph,
        name='customer_summary_overview_graph'),
    url(r'^customer-summary/overview-invoices/$', views.customer_summary_overview_invoices,
        name='customer_summary_overview_invoices'),
    url(r'^parties-export-excel$', views.parties_export_excel,
        name='parties_export_excel'),
]
