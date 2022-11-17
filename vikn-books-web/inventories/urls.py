from django.conf.urls import  url,include
from inventories import views


app_name = "inventories"

urlpatterns = [
    url(r'create-brand/',views.create_brand, name="create_brand"),
    url(r'brands/',views.brands, name="brands"),
    url(r'^view/brand/(?P<pk>.*)/$', views.view_brand, name='view_brand'),
    url(r'^edit-brand/(?P<pk>.*)/$', views.edit_brand, name='edit_brand'),
    url(r'^delete-brand/(?P<pk>.*)/$', views.delete_brand, name='delete_brand'),

    url(r'create-kitchen/',views.create_kitchen, name="create_kitchen"),
    url(r'kitchens/',views.kitchens, name="kitchens"),
    url(r'^view-kitchen/(?P<pk>.*)/$', views.view_kitchen, name='view_kitchen'),
    url(r'^edit-kitchen/(?P<pk>.*)/$', views.edit_kitchen, name='edit_kitchen'),
    url(r'^delete-kitchen/(?P<pk>.*)/$', views.delete_kitchen, name='delete_kitchen'),
    
    url(r'create-flavour/',views.create_flavour, name="create_flavour"),
    url(r'flavours/',views.flavours, name="flavours"),
    url(r'^view-flavour/(?P<pk>.*)/$', views.view_flavour, name='view_flavour'),
    url(r'^edit-flavour/(?P<pk>.*)/$', views.edit_flavour, name='edit_flavour'),
    url(r'^delete-flavour/(?P<pk>.*)/$', views.delete_flavour, name='delete_flavour'),

    url(r'create-route/',views.create_route, name="create_route"),
    url(r'routes/',views.routes, name="routes"),
    url(r'^view-route/(?P<pk>.*)/$', views.view_route, name='view_route'),
    url(r'^edit-route/(?P<pk>.*)/$', views.edit_route, name='edit_route'),
    url(r'^delete-route/(?P<pk>.*)/$', views.delete_route, name='delete_route'),

    url(r'create-warehouse/',views.create_warehouse, name="create_warehouse"),
    url(r'warehouses/',views.warehouses, name="warehouses"),
    url(r'^view-warehouse/(?P<pk>.*)/$', views.view_warehouse, name='view_warehouse'),
    url(r'^edit-warehouse/(?P<pk>.*)/$', views.edit_warehouse, name='edit_warehouse'),
    url(r'^delete-warehouse/(?P<pk>.*)/$', views.delete_warehouse, name='delete_warehouse'),

    url(r'create-product/',views.create_product, name="create_product"),
    url(r'products/',views.products, name="products"),
    url(r'^product/(?P<pk>.*)/$', views.product, name='product'),
    url(r'^edit-product/(?P<pk>.*)/$', views.edit_product, name='edit_product'),
    url(r'^delete-product/(?P<pk>.*)/$', views.delete_product, name='delete_product'),

    url(r'create-productGroup/',views.create_productGroup, name="create_productGroup"),
    url(r'productGroups/',views.productGroups, name="productGroups"),
    url(r'^view-productGroup/(?P<pk>.*)/$', views.view_productGroup, name='view_productGroup'),
    url(r'^edit-productGroup/(?P<pk>.*)/$', views.edit_productGroup, name='edit_productGroup'),
    url(r'^delete-productGroup/(?P<pk>.*)/$', views.delete_productGroup, name='delete_productGroup'),

    url(r'create-taxCategory/',views.create_taxCategory, name="create_taxCategory"),
    url(r'taxCategories/',views.taxCategories, name="taxCategories"),
    url(r'^view-taxCategory/(?P<pk>.*)/$', views.view_taxCategory, name='view_taxCategory'),
    url(r'^edit-taxCategory/(?P<pk>.*)/$', views.edit_taxCategory, name='edit_taxCategory'),
    url(r'^delete-taxCategory/(?P<pk>.*)/$', views.delete_taxCategory, name='delete_taxCategory'),
    
    url(r'priceCategories/',views.priceCategories, name="priceCategories"),
    url(r'^view-priceCategory/(?P<pk>.*)/$', views.view_priceCategory, name='view_priceCategory'),

    url(r'create-productCategory/',views.create_productCategory, name="create_productCategory"),
    url(r'productCategories/',views.productCategories, name="productCategories"),
    url(r'^view-productCategory/(?P<pk>.*)/$', views.view_productCategory, name='view_productCategory'),
    url(r'^edit-productCategory/(?P<pk>.*)/$', views.edit_productCategory, name='edit_productCategory'),
    url(r'^delete-productCategory/(?P<pk>.*)/$', views.delete_productCategory, name='delete_productCategory'),

    url(r'create-purchaseInvoice/',views.create_purchaseInvoice, name="create_purchaseInvoice"),
    url(r'purchaseInvoices/',views.purchaseInvoices, name="purchaseInvoices"),
    url(r'^edit-purchaseInvoice/(?P<pk>.*)/$', views.edit_purchaseInvoice, name='edit_purchaseInvoice'),

    url(r'get-unitPrice/$',views.get_unitPrice,name="get_unitPrice"),
    url(r'get-amount/$',views.get_amount,name="get_amount"),
    url(r'get-purchaseDetails/$',views.get_purchaseDetails,name="get_purchaseDetails"),
    url(r'post-purchaseEdited/$',views.post_purchaseEdited,name="post_purchaseEdited"),


]