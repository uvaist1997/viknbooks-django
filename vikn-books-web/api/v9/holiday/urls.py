from django.conf.urls import url, include
from api.v9.holiday import views


urlpatterns = [
    url(r'^create-holiday/$', views.create_holiday,
        name='create_holiday'),
    url(r'^holidays/$', views.holidays, name='holidays'),
    url(r'^view/holiday/(?P<pk>.*)/$',
        views.holiday, name='holiday'),
    url(r'^edit/holiday/(?P<pk>.*)/$',
        views.edit_holiday, name='edit_holiday'),
    url(r'^delete/holiday/(?P<pk>.*)/$',
        views.delete_holiday, name='delete_holiday'),

]
