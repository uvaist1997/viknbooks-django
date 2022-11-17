from django.conf.urls import url, include
from api.v10.stockManagements import views


urlpatterns = [
    url(r'^create-stockManagements/$', views.create_stockManagements,
        name='create_stockManagements'),
    url(r'^stockManagement-pagination/$', views.stockManagement_pagination, name='stockManagement_pagination'),
    url(r'^delete/stockManagement/(?P<pk>.*)/$',
        views.delete_stockManagement, name='delete_stockManagement'),
    url(r'^view/stockManagement/(?P<pk>.*)/$',
        views.view_stockManagement, name='view_stockManagement'),
    url(r'^edit/stockManagement/(?P<pk>.*)/$',
        views.edit_stockManagement, name='edit_stockManagement')
]
