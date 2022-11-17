from django.conf.urls import url, include
from api.v5.accountGroups import views


urlpatterns = [
    url(r'^create-accountGroup/$', views.create_accountGroup,
        name='create_accountGroup'),
    url(r'^accountGroups/$', views.accountGroups, name='accountGroups'),
    url(r'^view/accountGroup/(?P<pk>.*)/$',
        views.accountGroup, name='accountGroup'),
    url(r'^edit/accountGroup/(?P<pk>.*)/$',
        views.edit_accountGroup, name='edit_accountGroup'),
    url(r'^delete/accountGroup/(?P<pk>.*)/$',
        views.delete_accountGroup, name='delete_accountGroup'),

    url(r'^search-accountGroups/$', views.search_accountGroups,
        name='search_accountGroups'),
]
