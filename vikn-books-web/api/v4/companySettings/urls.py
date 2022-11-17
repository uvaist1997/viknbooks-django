from django.conf.urls import url, include
from api.v4.companySettings import views


urlpatterns = [
    url(r'^view/companySettings/$', views.companySettings, name='companySettings'),
    url(r'^edit/companySettings/$', views.edit_companySettings,
        name='edit_companySettings'),
    url(r'^create/companySettings/$', views.create_companySettings,
        name='create_companySettings'),
    url(r'^create/companySettingsCreate/$', views.create_companySettings_initial,
        name='create_companySettings_initial'),
    url(r'^delete/companySettings/(?P<pk>.*)/$',
        views.delete_companySettings, name='delete_companySettings'),
    url(r'^delete/companyPermanantly/(?P<pk>.*)/$',
        views.delete_companyPermanantly, name='delete_companyPermanantly'),
    url(r'^delete/companyTransactions/(?P<pk>.*)/$',
        views.delete_companyTransactions, name='delete_companyTransactions'),

    url(r'^check-company-delete/$', views.check_company_delete,
        name='check_company_delete'),

    url(r'^get-company-count/$', views.get_company_count,
        name='get_company_count'),
]
