from datetime import date

from django.db.models import Q

from branch.models import Location
from mobile.get_user import get_user
from permissions.functions.CheckUserPermissions import check_user_permissions
from permissions.models import ManyBranch
from user.functions.functions import check_auth
from user.models import CustomUser
from teachers.models import Teacher

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
            user, auth_error = check_auth(request)
            if auth_error:
                return auth_error
            if hasattr(self, 'table_names') and self.table_names:
                table_names = self.table_names
                permissions = check_user_permissions(user, table_names)
                if isinstance(response.data, dict):
                    response.data['permissions'] = custom_message
                if isinstance(response.data, list):
                    response.data.append(permissions)

            if isinstance(response.data, dict):
                response.data['msg'] = custom_message
            if isinstance(response.data, list):
                response.data.append([custom_message])
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
            'value': ['new_students', 'studying_students', 'deleted_students']
        },
        {
            'name': 'Teachers',
            'value': ['new_teacher', 'deleted_teacher', 'teacher']
        }
    ]

    def get_models(self, query_type):
        response = []
        if query_type:
            for item in query_type:
                data = {
                    'models': [],
                    'types': [item['type']],
                    'return': [item['name']]
                }
                for table in self.tables:
                    if item['type'].strip() in table['value']:
                        data['models'].append(table['name'])
                response.append(data)
        return response

    def filter(self):

        locations = self.request.data['locations']
        table_names = self.get_models(self.request.data['types'])
        datas = []

        location_objs = self.get_location_objs(locations)

        for model_info in table_names:
            for model in model_info['models']:
                # model_data = []
                # datas.append(model_data)
                for type_index, type_name in enumerate(model_info['types']):
                    type_data = {
                        'name': model_info['return'][type_index],
                        'list': []
                    }
                    datas.append(type_data)

                    for location in location_objs:
                        location_data = self.get_location_data(location, type_name, model)
                        type_data['list'].append(location_data)

        return datas

    def get_location_objs(self, location_ids):
        return Location.objects.filter(id__in=location_ids).all()

    def get_location_data(self, location, type_name, model):
        user, auth_error = check_auth(self.request)
        if auth_error:
            return auth_error
        location_data = {
            'id': location.id,
            'name': location.name,
            'count': location.branch_set.count(),
            'list': []
        }

        for branch in ManyBranch.objects.filter(user=user, branch__location_id=location.id).all():
            branch_data = self.get_branch_data(branch, type_name, model)
            location_data['list'].append(branch_data)

        return location_data

    def get_branch_data(self, branch, type_name, model):
        branch_data = {
            'id': branch.branch.id,
            'name': branch.branch.name,
            'count': 0
        }
        self.get_student_data(branch, type_name, branch_data, model)

        return branch_data

    def get_student_data(self, branch, type_name, branch_data, model):
        from students.models import DeletedStudent, DeletedNewStudent, Student
        if model == 'Students':
            deleted_student_ids = DeletedStudent.objects.values_list('student_id', flat=True)
            deleted_new_student_ids = DeletedNewStudent.objects.values_list('student_id', flat=True)

            if type_name == 'new_students':
                branch_data['count'] = Student.objects.filter(user__branch_id=branch.id).exclude(
                    id__in=deleted_student_ids).exclude(id__in=deleted_new_student_ids
                                                        ).filter(groups_student__isnull=True).count()
            elif type_name == 'studying_students':
                branch_data['count'] = Student.objects.filter(user__branch_id=branch.id).exclude(
                    id__in=deleted_student_ids).exclude(id__in=deleted_new_student_ids
                                                        ).filter(groups_student__isnull=False).count()
            elif type_name == 'deleted_students':
                branch_data['count'] = Student.objects.filter(user__branch_id=branch.id).exclude(
                    id__in=deleted_new_student_ids).count()
        if model == 'Teachers':
            if type_name == 'new_teacher':
                branch_data['count'] = Teacher.objects.filter(user__branch_id=branch.id).count()


