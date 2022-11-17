from django.conf.urls import url, include
from api.v3.states import views


urlpatterns = [
    url(r'^create-state/$', views.create_state, name='create_state'),
    url(r'^states/$', views.states, name='states'),
    url(r'^country-states/(?P<pk>.*)/$',
        views.country_state, name='country_state'),
    url(r'^view/state/(?P<pk>.*)/$', views.state, name='state'),
    url(r'^edit/state/(?P<pk>.*)/$', views.edit_state, name='edit_state'),
    url(r'^delete/state/(?P<pk>.*)/$', views.delete_state, name='delete_state'),
]
