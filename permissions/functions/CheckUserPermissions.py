from django.contrib.auth.models import Permission


def check_user_permissions(user, table_names):
    base_permissions_data = Permission.objects.filter(content_type__model__in=table_names)
    base_permissions = [permission.codename for permission in base_permissions_data]

    groups = user.groups.filter(permissions__content_type__model__in=table_names)
    user_permissions = [permission.codename for group in groups for permission in group.permissions.all()]

    fl_pr = {pr: pr in user_permissions for pr in base_permissions}

    return fl_pr
