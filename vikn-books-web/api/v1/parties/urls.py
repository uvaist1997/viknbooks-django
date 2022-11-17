from django.conf.urls import url,include
from api.v1.parties import views


urlpatterns = [
	url(r'^create-party/$', views.create_party, name='create_party'),
    url(r'^parties/$', views.parties, name='parties'),
    url(r'^view/party/(?P<pk>.*)/$', views.party, name='party'),
    url(r'^edit/party/(?P<pk>.*)/$', views.edit_party, name='edit_party'),
    url(r'^delete/party/(?P<pk>.*)/$', views.delete_party, name='delete_party'),
]