from django.conf.urls import url, include
from api.v7.loanType import views


urlpatterns = [
    url(r'^create-loanType/$', views.create_loanType,
        name='create_loanType'),
    url(r'^loanTypes/$', views.loanTypes, name='loanTypes'),
    url(r'^view/loanType/(?P<pk>.*)/$',
        views.loanType, name='loanType'),
    url(r'^edit/loanType/(?P<pk>.*)/$',
        views.edit_loanType, name='edit_loanType'),
    url(r'^delete/loanType/(?P<pk>.*)/$',
        views.delete_loanType, name='delete_loanType'),


]
