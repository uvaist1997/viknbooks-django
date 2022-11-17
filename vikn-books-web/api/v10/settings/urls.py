from django.conf.urls import url

from api.v10.settings import views

app_name = "api.v9.settings.urls"

urlpatterns = [
    url(r"^create-settings/$", views.create_settings, name="create_settings"),
    url(r"^list/settings/$", views.list_settings, name="list_settings"),
    url(
        r"^view/settings/(?P<pk>.*)/$",
        views.document_settings,
        name="document_settings",
    ),
    url(r"^edit/settings/(?P<pk>.*)/$", views.edit_settings, name="edit_settings"),
    url(
        r"^delete/settings/(?P<pk>.*)/$", views.delete_settings, name="delete_settings"
    ),
    url(r"^print-settings/$", views.print_settings, name="print_settings"),
    url(r"^barcode-settings/$", views.barcode_settings, name="barcode_settings"),
    url(r"^language/$", views.language, name="language"),
    url(
        r"^create-user-type-settings/$",
        views.create_user_type_settings,
        name="create_user_type_settings",
    ),
    url(
        r"^user-type-settings-list/$",
        views.user_type_settings_list,
        name="user_type_settings_list",
    ),
    url(r"^print-paper/$", views.print_paper, name="print_paper"),
    url(r"^print-paper-new/$", views.print_paper_new, name="print_paper_new"),
    url(r"^print-template/$", views.print_template, name="print_template"),
    url(
        r"^print-settings-list/$", views.print_settings_list, name="print_settings_list"
    ),
    url(r"^print-report-paper/$", views.print_report_paper, name="print_report_paper"),
    url(
        r"^user-role/settings-update/$",
        views.user_role_settings_update,
        name="user_role_settings_update",
    ),
    url(r"^user-role/settings/$", views.user_role_settings, name="user_role_settings"),
    url(r"^convert-to-image$", views.convert_to_image, name="convert_to_image"),
    url(r"^print-thermal$", views.print_thermal, name="print_thermal"),
    url(
        r"^report-export-to-excel",
        views.report_export_to_excel,
        name="report_export_to_excel",
    ),
    url(
        r"^user-role/settings/list-api/$",
        views.user_role_settings_list_api,
        name="user_role_settings_list_api",
    ),
]
