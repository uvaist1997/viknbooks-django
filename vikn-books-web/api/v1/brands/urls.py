from django.conf.urls import url,include
from api.v1.brands import views


urlpatterns = [
	url(r'^create-brand/$', views.create_brand, name='create_brand'),
    url(r'^brands/$', views.brands, name='brands'),
    url(r'^view/brand/(?P<pk>.*)/$', views.brand, name='brand'),
    url(r'^edit/brand/(?P<pk>.*)/$', views.edit_brand, name='edit_brand'),
    url(r'^delete/brand/(?P<pk>.*)/$', views.delete_brand, name='delete_brand'),

    url(r'^runAPIforChangeDatasInDBView/$', views.runAPIforChangeDatasInDBView, name='runAPIforChangeDatasInDBView'),


    url(r'^torunqryforBugFix/$', views.torunqryforBugFix, name='torunqryforBugFix'),
]