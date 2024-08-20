from django.contrib.auth.models import Permission, Group

from ..serializers import ManySystemRead, ManyLocationRead, ManyBranchRead


def check_user_permissions(user, table_names):
    system = user.branch.location.system.id
    many_systems = user.many_systems.all()
    system_serializers = ManySystemRead(many_systems, many=True)
    many_branches = user.many_branches.all()
    branch_serializers = ManyBranchRead(many_branches, many=True)
    many_locations = user.many_locations.all()
    location_serializers = ManyLocationRead(many_locations, many=True)
    base_permissions = Permission.objects.filter(content_type__model__in=table_names).values_list('codename', flat=True)

    user_permissions = user.groups.filter(permissions__content_type__model__in=table_names,
                                          authgroupsystem__system_id=system).values_list('permissions__codename',
                                                                                         flat=True)
    roles = Group.objects.all()
    jobs = []
    for role in roles:
        jobs.append({role.name: role.name in user.groups.values_list('name', flat=True)})
    return {pr: pr in user_permissions for pr in base_permissions}, {
        "system": system_serializers.data,
        "many_branches": branch_serializers.data,
        "many_locations": location_serializers.data,
        'jobs': jobs
    }
