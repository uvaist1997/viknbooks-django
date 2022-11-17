from django.conf.urls import url, include
from api.v8.loanRequest import views


urlpatterns = [
    url(r'^create-loanRequest/$', views.create_loanRequest,
        name='create_loanRequest'),
    url(r'^loanRequests/$', views.loanRequests, name='loanRequests'),
    url(r'^view/loanRequest/(?P<pk>.*)/$',
        views.loanRequest, name='loanRequest'),
    url(r'^edit/loanRequest/(?P<pk>.*)/$',
        views.edit_loanRequest, name='edit_loanRequest'),
    url(r'^delete/loanRequest/(?P<pk>.*)/$',
        views.delete_loanRequest, name='delete_loanRequest'),

    url(r'^loanApprovals/$', views.loanApprovals, name='loanApprovals'),
    url(r'^approve/loanRequest/(?P<pk>.*)/$',
        views.approve_loanRequest, name='approve_loanRequest'),
]
