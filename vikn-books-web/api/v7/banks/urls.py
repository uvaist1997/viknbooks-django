from django.conf.urls import url, include
from api.v7.banks import views


urlpatterns = [
    url(r'^create-bank/$', views.create_bank, name='create_bank'),
    url(r'^banks/$', views.banks, name='banks'),
    url(r'^view/bank/(?P<pk>.*)/$', views.bank, name='bank'),
    url(r'^edit/bank/(?P<pk>.*)/$', views.edit_bank, name='edit_bank'),
    url(r'^delete/bank/(?P<pk>.*)/$', views.delete_bank, name='delete_bank'),
]
