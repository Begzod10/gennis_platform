from django.apps import apps

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from ...models import DescriptionForTable


def get_permissions_for_table(table_name):
    model = None
    for m in apps.get_models():
        if m._meta.db_table == table_name:
            model = m
            break

    content_type = ContentType.objects.get_for_model(model)
    permissions = Permission.objects.filter(content_type=content_type)
    permissions_json = []
    for permission in permissions:
        permissions_json.append({'id': permission.pk, 'name': permission.name, 'codename': permission.codename})
    try:
        description = DescriptionForTable.objects.get(table_name=table_name)
        return {
            'permissions': permissions_json,
            'table_description': description.description
        }

    except DescriptionForTable.DoesNotExist:
        return {
            'permissions': permissions_json,
            'table_description': 'table haqida description mavjud emas'
        }
