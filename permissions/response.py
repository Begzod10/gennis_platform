from datetime import date
from urllib.parse import unquote

from django.db.models import Q

from mobile.get_user import get_user
from user.models import CustomUser


class CustomResponseMixin:
    def get_custom_message(self, request):

        method = request.method

        if method == 'GET':
            return f"maʼlumotlari muvaffaqiyatli olindi."
        elif method == 'POST':
            return f"  muvaffaqiyatli yaratildi."
        elif method == 'PUT':
            return f"  maʼlumotlari muvaffaqiyatli yangilandi."
        elif method == 'PATCH':
            return f"maʼlumotlari muvaffaqiyatli yangilandi."
        elif method == 'DELETE':
            return f" maʼlumotlari muvaffaqiyatli o'chirildi."
        else:
            return f"amal muvaffaqiyatli yakunlandi."

    def finalize_response(self, request, response, *args, **kwargs):

        response = super().finalize_response(request, response, *args, **kwargs)

        if 200 <= response.status_code < 300:
            custom_message = self.get_custom_message(request)
            if isinstance(response.data, dict):
                response.data['msg'] = custom_message

        return response


class QueryParamFilterMixin:
    filter_mappings = {}
    filter_conditions = Q()

    def filter_queryset(self, queryset):

        for param, field in self.filter_mappings.items():
            value = self.request.query_params.get(param)
            if value is not None:
                if '-' in value:
                    try:
                        age_from, age_to = map(int, value.split('-'))
                        if param == 'age':
                            today = date.today()
                            birth_date_from = date(today.year - age_to, today.month, today.day)
                            birth_date_to = date(today.year - age_from, today.month, today.day)
                            self.filter_conditions &= Q(**{f'{field}__range': (birth_date_from, birth_date_to)})
                        else:
                            self.filter_conditions &= Q(**{f'{field}__range': (age_from, age_to)})
                    except ValueError:
                        continue
                elif value.startswith('[') and value.endswith(']'):
                    value_list = [v.strip() for v in value.strip('[]').split(',')]
                    self.filter_conditions &= Q(**{f'{field}__in': value_list})
                elif value.isdigit():
                    self.filter_conditions &= Q(**{field: value})
                elif value == 'True' or value == 'False':
                    self.filter_conditions &= Q(**{field: value})
                else:
                    continue
            else:
                if param == 'branch':
                    user = CustomUser.objects.get(pk=get_user(self.request))
                    self.filter_conditions &= Q(**{field: user.branch_id})

        if self.filter_conditions:
            queryset = queryset.filter(self.filter_conditions)

        return queryset


class GetModelsMixin:
    tables = [
        {
            'name': 'Students',
            'value': ['new_student', 'studying_student', 'deleted_student']
        },
        {
            'name': 'Teachers',
            'value': ['new_teacher', 'deleted_teacher', 'teacher']
        }
    ]

    def get_models(self):
        response = []
        query_type = self.request.query_params.get('type')

        if query_type:
            query_type = unquote(query_type).strip('[]')

            query_type_list = query_type.split(',')

            for table in self.tables:
                if any(item.strip() in table['value'] for item in query_type_list):
                    response.append(table['name'])

        return response
