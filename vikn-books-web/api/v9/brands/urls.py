from django.conf.urls import include, url

from api.v9.brands import views

app_name = "api.v9.brands"

urlpatterns = [
    url(r"^create-brand/$", views.create_brand, name="create_brand"),
    url(r"^brands/$", views.brands, name="brands"),
    url(r"^view/brand/(?P<pk>.*)/$", views.brand, name="brand"),
    url(r"^edit/brand/(?P<pk>.*)/$", views.edit_brand, name="edit_brand"),
    url(r"^delete/brand/(?P<pk>.*)/$", views.delete_brand, name="delete_brand"),
    

    url(r"^torunqryTest/$", views.torunqryTest, name="torunqryTest"),
    url(
        r"^generate-random-users/$",
        views.generate_random_users,
        name="generate_random_users",
    ),
    url(r"^search-brands/$", views.search_brands, name="search_brands"),
    url(r"^setDefault-brands/$", views.setDefault_brands, name="setDefault_brands"),
    url(r"^search-brand-list/$", views.search_brand_list, name="search_brand_list"),
]
