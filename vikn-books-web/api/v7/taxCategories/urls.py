from django.conf.urls import url, include
from api.v7.taxCategories import views


urlpatterns = [
    url(r'^create-taxCategory/$', views.create_taxCategory,
        name='create_taxCategory'),
    url(r'^taxCategories/$', views.taxCategories, name='taxCategories'),
    url(r'^view/taxCategory/(?P<pk>.*)/$',
        views.taxCategory, name='taxCategory'),
    url(r'^edit/taxCategory/(?P<pk>.*)/$',
        views.edit_taxCategory, name='edit_taxCategory'),
    url(r'^delete/taxCategory/(?P<pk>.*)/$',
        views.delete_taxCategory, name='delete_taxCategory'),

    url(r'^taxListByType/$', views.taxListByType, name='taxListByType'),
    url(r'^get-tax-details/$', views.get_tax_details, name='get_tax_details'),
    url(r'^listTaxType/$', views.listTaxType, name='listTaxType'),
]
