from django.conf.urls import url, include
from api.v4.stockPostings import views


urlpatterns = [
    url(r'^create-stockPosting/$', views.create_stockPosting,
        name='create_stockPosting'),
    url(r'^stockPostings/$', views.stockPostings, name='stockPostings'),
    url(r'^view/stockPosting/(?P<pk>.*)/$',
        views.stockPosting, name='stockPosting'),
    url(r'^edit/stockPosting/(?P<pk>.*)/$',
        views.edit_stockPosting, name='edit_stockPosting'),
    url(r'^delete/stockPosting/(?P<pk>.*)/$',
        views.delete_stockPosting, name='delete_stockPosting'),

    url(r'^create-excess-stock/$', views.create_excess_stock,
        name='create_excess_stock'),
    url(r'^list-excessStock/$', views.list_excessStock, name='list_excessStock'),
    url(r'^delete/excessStock/(?P<pk>.*)/$',
        views.delete_excessStock, name='delete_excessStock'),
    url(r'^edit/excessStock/(?P<pk>.*)/$',
        views.edit_excessStock, name='edit_excessStock'),
    url(r'^view/excessStock/(?P<pk>.*)/$',
        views.excessStock, name='excessStock'),

    url(r'^create-shortage-stock/$', views.create_shortage_stock,
        name='create_shortage_stock'),
    url(r'^list-shortageStock/$', views.list_shortageStock,
        name='list_shortageStock'),
    url(r'^delete/shortageStock/(?P<pk>.*)/$',
        views.delete_shortageStock, name='delete_shortageStock'),
    url(r'^edit/shortageStock/(?P<pk>.*)/$',
        views.edit_shortageStock, name='edit_shortageStock'),
    url(r'^view/shortageStock/(?P<pk>.*)/$',
        views.shortageStock, name='shortageStock'),

    url(r'^create-damage-stock/$', views.create_damage_stock,
        name='create_damage_stock'),
    url(r'^list-damageStock/$', views.list_damageStock, name='list_damageStock'),
    url(r'^delete/damageStock/(?P<pk>.*)/$',
        views.delete_damageStock, name='delete_damageStock'),
    url(r'^edit/damageStock/(?P<pk>.*)/$',
        views.edit_damageStock, name='edit_damageStock'),
    url(r'^view/damageStock/(?P<pk>.*)/$',
        views.damageStock, name='damageStock'),

    url(r'^create-used-stock/$', views.create_used_stock, name='create_used_stock'),
    url(r'^list-usedStock/$', views.list_usedStock, name='list_usedStock'),
    url(r'^delete/usedStock/(?P<pk>.*)/$',
        views.delete_usedStock, name='delete_usedStock'),
    url(r'^edit/usedStock/(?P<pk>.*)/$',
        views.edit_usedStock, name='edit_usedStock'),
    url(r'^view/usedStock/(?P<pk>.*)/$', views.usedStock, name='usedStock'),
]
