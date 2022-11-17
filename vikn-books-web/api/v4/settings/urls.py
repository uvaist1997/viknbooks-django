from django.conf.urls import url, include
from api.v4.settings import views


app_name = 'api.v4.settings.urls'

urlpatterns = [
    url(r'^create-settings/$', views.create_settings, name='create_settings'),
    url(r'^list/settings/$', views.list_settings, name='list_settings'),
    url(r'^view/settings/(?P<pk>.*)/$', views.settings, name='settings'),
    url(r'^edit/settings/(?P<pk>.*)/$', views.edit_settings, name='edit_settings'),
    url(r'^delete/settings/(?P<pk>.*)/$',
        views.delete_settings, name='delete_settings'),
    url(r'^print-settings/$', views.print_settings, name='print_settings'),
    url(r'^barcode-settings/$', views.barcode_settings, name='barcode_settings'),
    url(r'^language/$', views.language, name='language'),
    url(r'^create-user-type-settings/$', views.create_user_type_settings,
        name='create_user_type_settings'),
    url(r'^user-type-settings-list/$', views.user_type_settings_list,
        name='user_type_settings_list'),
    # url(r'^print-view/(?P<pk>.*)/$', views.print_view, name='print_view'),
]
