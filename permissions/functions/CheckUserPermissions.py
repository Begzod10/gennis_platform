from django.contrib.auth.models import Permission


def check_user_permissions(user, table_names):
    system = user.branch.location.system.id
    many_systems = user.many_systems.all().values_list('system_id',
                                                       flat=True)

    base_permissions = Permission.objects.filter(content_type__model__in=table_names).values_list('codename', flat=True)

    user_permissions = user.groups.filter(permissions__content_type__model__in=table_names,
                                          authgroupsystem__system_id=system).values_list('permissions__codename',
                                                                                         flat=True)
    return {pr: pr in user_permissions for pr in base_permissions}
