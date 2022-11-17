from django.conf.urls import url

from api.v9.reportQuerys import views

urlpatterns = [
    url(r'^download-report/$', views.download_report, name='download_report'),
    url(r'^mail-report/$', views.send_mail_reports, name='send_mail_reports'),
   
]
