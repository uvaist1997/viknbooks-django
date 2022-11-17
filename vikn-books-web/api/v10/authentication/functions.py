from django.contrib.auth.models import User


def get_current_role(cls):
    current_role = "user"

    if cls.user.is_authenticated:
        roles = list(set([x.name for x in cls.user.groups.all()]))
        if cls.user.is_superuser:
            current_role = "superuser"
        elif "supplier" in roles:
            current_role = "supplier"
        elif "customer" in roles:
            current_role = "customer"

    return current_role
