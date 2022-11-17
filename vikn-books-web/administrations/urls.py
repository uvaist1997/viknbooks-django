from django.conf.urls import  url,include
from administrations import views


app_name = "administrations"

urlpatterns = [
    url(r'create-general-settings/',views.create_general_settings, name="create_general_settings"),
    url(r'create-user/',views.create_user, name="create_user"),
    url(r'users/',views.users, name="users"),
    url(r'^view-user/(?P<pk>.*)/$', views.view_user, name='view_user'),
    url(r'^edit-user/(?P<pk>.*)/$', views.edit_user, name='edit_user'),
    url(r'^delete-user/(?P<pk>.*)/$', views.delete_user, name='delete_user'),

    url(r'create-user-type/',views.create_user_type, name="create_user_type"),
    url(r'user-types/',views.user_types, name="user_types"),
    url(r'^user-type/(?P<pk>.*)/$', views.user_type, name='user_type'),
    url(r'^edit-user-type/(?P<pk>.*)/$', views.edit_user_type, name='edit_user_type'),
    url(r'^delete-user-type/(?P<pk>.*)/$', views.delete_user_type, name='delete_user_type'),

    url(r'create-financial-year/',views.create_financial_year, name="create_financial_year"),
    url(r'financial-years/',views.financial_years, name="financial_years"),
    url(r'^financial-year/(?P<pk>.*)/$', views.financial_year, name='financial_year'),
    url(r'^edit-financial-year/(?P<pk>.*)/$', views.edit_financial_year, name='edit_financial_year'),
    url(r'^update-company-settings/(?P<pk>.*)/$', views.update_company_settings, name='update_company_settings'),
    url(r'^delete-financial-year/(?P<pk>.*)/$', views.delete_financial_year, name='delete_financial_year'),
]