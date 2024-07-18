from django.contrib.auth.models import Permission


def check_user_permissions(user, table_names):
    system = user.branch.location.system.id
    base_permissions_data = Permission.objects.filter(content_type__model__in=table_names)
    base_permissions = [permission.codename for permission in base_permissions_data]

    user_permissions = []
    groups = user.groups.filter(permissions__content_type__model__in=table_names)
    for group in groups:
        if group.authgroupsystem.system_id.id == system:
            user_permissions.extend(permission.codename for permission in group.permissions.all())

    fl_pr = {pr: pr in user_permissions for pr in base_permissions}
    return fl_pr
