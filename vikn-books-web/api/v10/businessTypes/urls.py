from django.conf.urls import include, url

from api.v10.businessTypes import views

urlpatterns = [
    url(
        r"^create-business-type/$",
        views.create_business_type,
        name="create_business_type",
    ),
    url(r"^business-types/$", views.business_types, name="business_types"),
    url(r"^business-type/(?P<pk>.*)/$", views.business_type, name="business_type"),
    url(
        r"^edit-business-type/(?P<pk>.*)/$",
        views.edit_business_type,
        name="edit_business_type",
    ),
    url(
        r"^delete-business-type/(?P<pk>.*)/$",
        views.delete_business_type,
        name="delete_business_type",
    ),
]
