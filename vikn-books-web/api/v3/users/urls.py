from django.conf.urls import url, include
from django.urls import path, include
from api.v3.users import views


urlpatterns = [
    url(r'^create-user/$', views.create_user, name='create_user'),
    url(r'^users/$', views.users, name='users'),
    url(r'^customers/$', views.customers, name='customers'),
    url(r'^user-types/$', views.user_types, name='user_types'),
    url(r'^view/user/(?P<pk>.*)/$', views.user, name='user'),
    url(r'^edit/user/(?P<pk>.*)/$', views.edit_user, name='edit_user'),
    url(r'^delete/user/(?P<pk>.*)/$', views.delete_user, name='delete_user'),

    url(r'^check-user/$', views.check_user, name='check_user'),
    url(r'^user-login/$', views.user_login, name='user_login'),
    url(r'^user-signup/$', views.user_signup, name='user_signup'),
    url(r'^companies/$', views.companies, name='companies'),
    url(r'^logout-view/$', views.logout_view, name='logout_view'),
    url(r'^create-company/$', views.create_company, name='create_company'),
    url(r'^user-accounts/$', views.user_accounts, name='user_accounts'),
    url(r'^update-user/$', views.update_user, name='update_user'),
    url(r'^user-view/(?P<pk>.*)/$', views.user_view, name='user_view'),

    url(r'^create-user-type/$', views.create_user_type, name='create_user_type'),
    url(r'^userTypes/$', views.userTypes, name='userTypes'),
    url(r'^view/userType/(?P<pk>.*)/$', views.userType, name='userType'),
    url(r'^edit/userType/(?P<pk>.*)/$', views.edit_userType, name='edit_userType'),
    url(r'^delete/userType/(?P<pk>.*)/$',
        views.delete_userType, name='delete_userType'),

    url(r'^create-general-settings/$', views.create_general_settings,
        name='create_general_settings'),
    url(r'^general-settings-list/$', views.general_settings_list,
        name='general_settings_list'),

    url(r'^get-default-values/$', views.get_defaults, name='get_defaults'),

    url(r'^activity-logs/$', views.activity_logs, name='activity_logs'),
    url(r'^activity-log/(?P<pk>.*)/$', views.activity_log, name='activity_log'),
    url(r'^create-software-version/$', views.create_software_version, name='create_software_version'),
    url(r'^software-versions/$', views.software_versions, name='software_versions'),
    url(r'^software_version/$', views.software_version, name='software_version'),


]
