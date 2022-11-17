from django.conf.urls import url, include
from api.v9.category import views

urlpatterns = [
    url(r'^create-category/$', views.create_category, name='create_category'),
    url(r'^edit-category/(?P<pk>.*)/$', views.edit_category, name='edit_category'),
    url(r'^categories/$', views.categories, name='categories'),
    url(r'^category/(?P<pk>.*)/$', views.category, name='category'),
    url(r'^delete-category/(?P<pk>.*)/$',
        views.delete_category, name='delete_category'),

    url(r'^create-database-sync/$', views.create_database_sync,
        name='create_database_sync'),
    url(r'^edit-database-sync/(?P<pk>.*)/$',
        views.edit_database_sync, name='edit_database_sync'),
    url(r'^database-sync-list/$', views.database_sync_list,
        name='database_sync_list'),
    url(r'^database-sync/$', views.database_sync, name='database_sync'),
]
