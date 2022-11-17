from django.conf.urls import url, include
from django.urls import path, include, re_path
from api.v8.users import views


urlpatterns = [
    url(r'^create-user/$', views.create_user, name='create_user'),
    url(r'^users/$', views.users, name='users'),
    url(r'^customers/$', views.customers, name='customers'),
    url(r'^user-types/$', views.user_types, name='user_types'),
    url(r'^view/user/(?P<pk>.*)/$', views.user, name='user'),
    url(r'^edit/user/(?P<pk>.*)/$', views.edit_user, name='edit_user'),
    url(r'^delete/user/(?P<pk>.*)/$', views.delete_user, name='delete_user'),

    url(r'^check-user/$', views.check_user, name='check_user'),
    # url(r'^user-login/$', views.user_login, name='user_login'),
    url(r'^user-login/$', views.user_login, name='user_login'),
    url(r'^check-username/$', views.check_username, name='check_username'),
    url(r'^user-login/admins/$', views.user_login_admins, name='user_login_admins'),
    url(r'^user-signup/$', views.user_signup, name='user_signup'),
    url(r'^signup-verified/$', views.signUp_verified, name='signUp_verified'),
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
    url(r'^activity-log-solve/$', views.activity_log_solve,
        name='activity_log_solve'),
    url(r'^activity-log/(?P<pk>.*)/$', views.activity_log, name='activity_log'),
    url(r'^create-software-version/$', views.create_software_version,
        name='create_software_version'),
    url(r'^software-versions/$', views.software_versions, name='software_versions'),
    url(r'^software_version/$', views.software_version, name='software_version'),

    url(r'^users-list/$', views.user_list, name='user_list'),
    url(r'^users-list-filter/$', views.user_list_filter, name='user_list_filter'),
    url(r'^switch-company/$', views.switch_company, name='switch_company'),
    url(r'^get-user-table/$', views.get_user_table, name='get_user_table'),
    url(r'^get-financial-year/$', views.get_financial_year, name='get_financial_year'),
    url(r'^get-company-details/$', views.get_company_details, name='get_company_details'),

    url(r'^get-last/user/token/$', views.get_last_user_token, name='get_last_user_token'),
    url(r'^forgot-password/$', views.forgot_password, name='forgot_password'),
    url(r'^forgot-password-confirm/(?P<uidb64>.*)/(?P<token>.*)/$',views.forgot_password_confirm, name='forgot_password_confirm'),

    url(r'^user-mobileup/$', views.mobile_signup, name='mobile_signup'),

    url(r'^user-invite/$', views.user_invite, name='user_invite'),
    url(r'^render-one-time-template/$', views.render_one_time_template, name='render_one_time_template'),

    url(r'^resend-verification-code/$', views.resend_verification_code, name='resend_verification_code'),

]
