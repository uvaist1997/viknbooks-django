from django.apps import AppConfig
class AccountsConfig(AppConfig):
    name = 'users'
    # This function is the only new thing in this file
    # it just imports the signal file when the app is ready
    def ready(self):
        import users.signals