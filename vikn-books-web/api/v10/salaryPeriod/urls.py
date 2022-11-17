from django.conf.urls import url, include
from api.v10.salaryPeriod import views


urlpatterns = [
    url(r'^create-salaryPeriod/$', views.create_salaryPeriod,
        name='create_salaryPeriod'),
    url(r'^salaryPeriods/$', views.salaryPeriods, name='salaryPeriods'),
    url(r'^view/salaryPeriod/(?P<pk>.*)/$',
        views.salaryPeriod, name='salaryPeriod'),
    url(r'^edit/salaryPeriod/(?P<pk>.*)/$',
        views.edit_salaryPeriod, name='edit_salaryPeriod'),
    url(r'^delete/salaryPeriod/(?P<pk>.*)/$',
        views.delete_salaryPeriod, name='delete_salaryPeriod'),

    # url(r'^create-department/$', views.create_department, name='create_department'),
    # url(r'^departments/$', views.departments, name='departments'),
    # url(r'^view/department/(?P<pk>.*)/$', views.department, name='department'),
    # url(r'^edit/department/(?P<pk>.*)/$', views.edit_department, name='edit_department'),
    # url(r'^delete/department/(?P<pk>.*)/$', views.delete_department, name='delete_department'),
]
