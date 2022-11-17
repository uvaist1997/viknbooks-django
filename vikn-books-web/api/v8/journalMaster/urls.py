from django.conf.urls import url, include
from api.v8.journalMaster import views


urlpatterns = [
    url(r'^create-journalMaster/$', views.create_journalMaster,
        name='create_journalMaster'),
    url(r'^journalMasters/$', views.journalMasters, name='journalMasters'),
    url(r'^view/journalMaster/(?P<pk>.*)/$',
        views.journalMaster, name='journalMaster'),
    url(r'^edit/journalMaster/(?P<pk>.*)/$',
        views.edit_journalMaster, name='edit_journalMaster'),
    url(r'^delete/journalMaster/(?P<pk>.*)/$',
        views.delete_journalMaster, name='delete_journalMaster'),
]
