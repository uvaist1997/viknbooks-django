from django.conf.urls import url, include
from api.v4.countries import views


urlpatterns = [
    url(r'^create-country/$', views.create_country, name='create_country'),
    url(r'^countries/$', views.countries, name='countries'),
    url(r'^country-tax-type/(?P<pk>.*)/$',
        views.country_tax_type, name='country_tax_type'),
    url(r'^view/country/(?P<pk>.*)/$', views.country, name='country'),
    url(r'^edit/country/(?P<pk>.*)/$', views.edit_country, name='edit_country'),
    url(r'^delete/country/(?P<pk>.*)/$',
        views.delete_country, name='delete_country'),
]
