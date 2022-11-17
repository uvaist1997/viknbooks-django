from django.conf.urls import url, include
from api.v3.journals import views


urlpatterns = [
    url(r'^create-journal/$', views.create_journal, name='create_journal'),
    url(r'^journals/$', views.journals, name='journals'),
    url(r'^view/journal/(?P<pk>.*)/$', views.journal, name='journal'),
    url(r'^edit/journal/(?P<pk>.*)/$', views.edit_journal, name='edit_journal'),
    url(r'^delete/journalDetail/(?P<pk>.*)/$',
        views.delete_journalDetail, name='delete_journalDetail'),
    url(r'^delete/journal/(?P<pk>.*)/$',
        views.delete_journal, name='delete_journal'),
]
