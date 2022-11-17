from django.conf.urls import url, include
from api.v7.states import views


urlpatterns = [
    url(r'^create-state/$', views.create_state, name='create_state'),
    url(r'^states/$', views.states, name='states'),
    url(r'^country-states/(?P<pk>.*)/$',
        views.country_state, name='country_state'),
    url(r'^get-state-detail/$', views.get_state_detail, name='get_state_detail'),
    url(r'^view/state/(?P<pk>.*)/$', views.state, name='state'),
    url(r'^edit/state/(?P<pk>.*)/$', views.edit_state, name='edit_state'),
    url(r'^delete/state/(?P<pk>.*)/$', views.delete_state, name='delete_state'),

    url(r'^create-UQC/$', views.create_UQC, name='create_UQC'),
    url(r'^view/UQC/(?P<pk>.*)/$', views.view_UQC, name='view_UQC'),
    url(r'^list-UQC/$', views.list_UQC, name='list_UQC'),
    url(r'^edit/UQC/(?P<pk>.*)/$', views.edit_UQC, name='edit_UQC'),
    url(r'^delete/UQC/(?P<pk>.*)/$', views.delete_UQC, name='delete_UQC'),
]
