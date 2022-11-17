from django.conf.urls import url, include
from api.v3.userTable import views


urlpatterns = [
    url(r'^create-user-table/$', views.create_user_table, name='create_user_table'),
    url(r'^user-tables/$', views.user_tables, name='user_tables'),
    url(r'^user-table/(?P<pk>.*)/$', views.user_table, name='user_table'),
    url(r'^edit-user-table/(?P<pk>.*)/$',
        views.edit_user_table, name='edit_user_table'),
    url(r'^delete-user-table/(?P<pk>.*)/$',
        views.delete_user_table, name='delete_user_table'),
    url(r'^leave-user-table/(?P<pk>.*)/$',
        views.leave_user_table, name='leave_user_table'),
]
