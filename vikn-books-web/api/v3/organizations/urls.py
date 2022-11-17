from django.conf.urls import url, include
from api.v3.organizations import views


urlpatterns = [
    url(r'^create-organization-settings/$',
        views.create_organization_settings, name='create_organization_settings'),
    url(r'^business-types/$', views.business_types, name='business_types'),
    url(r'^organization-user-list/$', views.organization_user_list,
        name='organization_user_list'),
    url(r'^organizations/$', views.organizations, name='organizations'),
    url(r'^organization-list/(?P<pk>.*)/$',
        views.organization_list, name='organization_list'),
    url(r'^business-type/(?P<pk>.*)/$', views.business_type, name='business_type'),
    url(r'^edit-organization/(?P<pk>.*)/$',
        views.edit_organization, name='edit_organization'),
    url(r'^delete-business-type/(?P<pk>.*)/$',
        views.delete_business_type, name='delete_business_type'),
]
