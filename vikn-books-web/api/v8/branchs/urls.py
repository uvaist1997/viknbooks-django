from django.conf.urls import url, include
from api.v8.branchs import views


urlpatterns = [
    url(r'^create-branch/$', views.create_branch, name='create_branch'),
    url(r'^regional-office-branchs/$', views.regional_office_branchs,
        name='regional_office_branchs'),
    url(r'^branchs/$', views.branchs, name='branchs'),
    url(r'^view/branch/(?P<pk>.*)/$', views.branch, name='branch'),
    url(r'^edit/branch/(?P<pk>.*)/$', views.edit_branch, name='edit_branch'),
    url(r'^delete/branch/(?P<pk>.*)/$', views.delete_branch, name='delete_branch'),
    # url(r'^get-batch-value/$', views.get_batch_value, name='get_batch_value'),
]
