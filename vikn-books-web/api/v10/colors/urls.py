from django.conf.urls import url, include
from api.v10.colors import views


urlpatterns = [
    url(r'^create-color/$', views.create_color, name='create_color'),
    url(r'^colors/$', views.colors, name='colors'),
    url(r'^view/color/(?P<pk>.*)/$', views.color, name='color'),
    url(r'^edit/color/(?P<pk>.*)/$', views.edit_color, name='edit_color'),
    url(r'^delete/color/(?P<pk>.*)/$', views.delete_color, name='delete_color'),

    url(r'^create-testImage/$', views.create_testImage, name='create_testImage'),
    url(r'^testImage-list/$', views.testImage_list, name='testImage_list'),

    url(r'^create-taskReact/$', views.create_taskReact, name='create_taskReact'),
    url(r'^taskReacts/$', views.taskReacts, name='taskReacts'),
    url(r'^view/taskReact/(?P<pk>.*)/$', views.taskReact, name='taskReact'),
    url(r'^edit/taskReact/(?P<pk>.*)/$',
        views.edit_taskReact, name='edit_taskReact'),
]
