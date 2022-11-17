from django.conf.urls import include, url

from api.v10.bankReconciliationStatement import views

app_name = "api.v9.bankReconciliationStatement"

urlpatterns = [
    url(
        r"^reconsiliation-create/$",
        views.reconsiliation_create,
        name="reconsiliation_create",
    ),
    url(
        r"^reconsiliation-details/$",
        views.reconsiliation_details,
        name="reconsiliation_details",
    ),
    url(
        r"^reconsiliation-list/$", views.reconsiliation_list, name="reconsiliation_list"
    ),
    url(
        r"^delete/reconsiliation/(?P<pk>.*)/$",
        views.delete_reconsiliation,
        name="delete_reconsiliation",
    ),
    url(r"^bank-list/$", views.bank_list, name="bank_list"),
    url(
        r"^view/reconsiliation/(?P<pk>.*)/$",
        views.view_reconsiliation,
        name="view_reconsiliation",
    ),
    url(
        r"^edit/reconsiliation/(?P<pk>.*)/$",
        views.edit_reconsiliation,
        name="edit_reconsiliation",
    ),
    url(
        r"^undo/reconsiliation/(?P<pk>.*)/$",
        views.undo_reconsiliation,
        name="undo_reconsiliation",
    ),
    url(
        r"^search-reconsiliation-list/$",
        views.search_reconsiliation_list,
        name="search_reconsiliation_list",
    ),
    url(
        r"^bank-reconsiliation-report/$",
        views.bank_reconsiliation_report,
        name="bank_reconsiliation_report",
    ),
]
