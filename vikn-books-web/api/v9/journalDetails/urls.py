from django.conf.urls import url, include
from api.v9.journalDetails import views


urlpatterns = [
    url(r'^create-journalDetail/$', views.create_journalDetail,
        name='create_journalDetail'),
    url(r'^journalDetails/$', views.journalDetails, name='journalDetails'),
    url(r'^view/journalDetail/(?P<pk>.*)/$',
        views.journalDetail, name='journalDetail'),
    url(r'^edit/journalDetail/(?P<pk>.*)/$',
        views.edit_journalDetail, name='edit_journalDetail'),
    url(r'^delete/journalDetail/(?P<pk>.*)/$',
        views.delete_journalDetail, name='delete_journalDetail'),

    url(r'^create-journalDetailsDummy/$', views.create_journalDetailsDummy,
        name='create_journalDetailsDummy'),
    url(r'^list/journalDetailsDummy/$', views.list_journalDetailsDummy,
        name='list_journalDetailsDummy'),
    url(r'^edit/journalDetailsDummy/(?P<pk>.*)/$',
        views.edit_journalDetailsDummy, name='edit_journalDetailsDummy'),
    url(r'^delete/journalDetailsDummy/(?P<pk>.*)/$',
        views.delete_journalDetailsDummy, name='delete_journalDetailsDummy'),

    url(r'^create-DummyforEditJournalMaster/$',
        views.create_DummyforEditJournalMaster, name='create_DummyforEditJournalMaster'),
]
