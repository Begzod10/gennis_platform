from datetime import date

from django.db.models import Q
from rest_framework import permissions

from mobile.get_user import get_user
from permissions.models import ManyBranch, ManyLocation
from user.functions.functions import check_auth


class CustomResponseMixin:
    def get_custom_message(self, method):
        messages = {'POST': "muvaffaqiyatli yaratildi.", 'PUT': "maʼlumotlari muvaffaqiyatli yangilandi.",
                    'PATCH': "maʼlumotlari muvaffaqiyatli yangilandi.",
                    'DELETE': "maʼlumotlari muvaffaqiyatli o'chirildi.", }
        return messages.get(method, "amal muvaffaqiyatli yakunlandi.")

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)

        if not (200 <= response.status_code < 300 and isinstance(response.data, (dict, list))):
            return response
        custom_message = self.get_custom_message(request.method)
        if isinstance(response.data, dict):
            response.data['msg'] = custom_message
        elif isinstance(response.data, list):
            response.data = {'msg': custom_message, }
        return response


class QueryParamFilterMixin:
    filter_mappings = {}
    filter_conditions = Q()

    def filter_queryset(self, queryset):
        query_params = self.request.query_params

        for param, field in self.filter_mappings.items():
            value = query_params.get(param)
            if not value or value == 'null':
                if param == 'branch':
                    user = get_user(self.request)
                    self.filter_conditions &= Q(**{field: user.branch_id})
                continue

            if param == 'age' and '-' in value:
                try:
                    age_from, age_to = map(int, value.split('-'))
                    today = date.today()
                    birth_date_from = date(today.year - age_to, today.month, today.day)
                    birth_date_to = date(today.year - age_from, today.month, today.day)
                    self.filter_conditions &= Q(**{f'{field}__range': (birth_date_from, birth_date_to)})
                except ValueError:
                    continue
            elif param == "seats_number" and "-" in value:
                try:
                    from_seat, to_seat = map(int, value.split('-'))
                    self.filter_conditions &= Q(**{field + "__gte": from_seat}) & Q(**{field + "__lte": to_seat})
                except ValueError:
                    continue

            elif value.startswith('[') and value.endswith(']'):
                value_list = value.strip('[]').split(',')
                self.filter_conditions &= Q(**{f'{field}__in': [v.strip() for v in value_list]})
            elif value.isdigit():
                self.filter_conditions &= Q(**{field: value})
            elif value in ['True', 'False']:
                self.filter_conditions &= Q(**{field: value == 'True'})

        if self.filter_conditions:
            queryset = queryset.filter(self.filter_conditions)

        # Muhim: DRF filter_backends (SearchFilter, OrderingFilter, va hokazo) ni ham ishlatish
        return super().filter_queryset(queryset)


class GetModelsMixin:
    tables = [{'name': 'Students', 'value': ['new_students', 'studying_students', 'deleted_students']},
              {'name': "Lead", 'value': ['leads']}, {'name': 'Group', 'value': ['groups']},
              {'name': 'Teacher', 'value': ['teachers']}, {'name': 'Users', 'value': ['worker']},
              {'name': 'Rooms', 'value': ['rooms']}, {'name': 'Accounting',
                                                      'value': ['studentsPayments', 'teachersSalary', 'employeesSalary',
                                                                'overhead', 'capital']}]

    def get_models(self, query_type):
        response = []
        if query_type:
            for item in query_type:
                data = {'models': [], 'types': [item['type']], 'return': [item['name']]}
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
                for type_index, type_name in enumerate(model_info['types']):
                    type_data = {'name': model_info['return'][type_index], 'type': type_name, 'list': []}
                    datas.append(type_data)

                    for location in location_objs:
                        location_data = self.get_location_data(location, type_name, model)
                        type_data['list'].append(location_data)

        return datas

    def get_location_objs(self, location_ids):
        user, auth_error = check_auth(self.request)
        if auth_error:
            return auth_error
        return ManyLocation.objects.filter(user=user, location_id__in=location_ids).all()

    def get_location_data(self, location, type_name, model):
        user, auth_error = check_auth(self.request)
        if auth_error:
            return auth_error
        location_data = {'id': location.location.id, 'name': location.location.name,
                         'count': ManyBranch.objects.filter(user=user,
                                                            branch__location_id=location.location.id).count(),
                         'list': []}

        for branch in ManyBranch.objects.filter(user=user, branch__location_id=location.location.id).all():
            branch_data = self.get_branch_data(branch, type_name, model)
            location_data['list'].append(branch_data)

        return location_data

    def get_branch_data(self, branch, type_name, model):
        branch_data = {'id': branch.branch.id, 'name': branch.branch.name, 'count': 0, 'summa': 0, 'deleted_count': 0}
        self.get_student_data(branch.branch, type_name, branch_data, model)

        return branch_data

    def get_student_data(self, branch, type_name, branch_data, model):
        from students.models import DeletedStudent, DeletedNewStudent, Student
        if model == 'Students':
            deleted_student_ids = DeletedStudent.objects.filter(deleted=False).values_list('student_id', flat=True)
            deleted_new_student_ids = DeletedNewStudent.objects.values_list('student_id', flat=True)

            if type_name == 'new_students':
                branch_data['count'] = Student.objects.filter(user__branch_id=branch.id).exclude(
                    id__in=deleted_student_ids).exclude(id__in=deleted_new_student_ids).filter(
                    groups_student__isnull=True).count()
                branch_data['deleted_count'] = deleted_new_student_ids.count()
            elif type_name == 'studying_students':
                deleted_student_ids = DeletedStudent.objects.filter(student__groups_student__isnull=True, deleted=False,
                                                                    student__user__branch_id=branch.id).values_list(
                    'student_id', flat=True)
                deleted_new_student_ids = DeletedNewStudent.objects.values_list('student_id', flat=True)
                active_students = Student.objects.exclude(id__in=deleted_student_ids).exclude(
                    id__in=deleted_new_student_ids).filter(groups_student__isnull=False,
                                                           user__branch_id=branch.id).distinct().order_by(
                    'class_number__number')
                branch_data['count'] = active_students.count()
            elif type_name == 'deleted_students':
                branch_data['count'] = Student.objects.filter(user__branch_id=branch.id,
                                                              groups_student__isnull=True).exclude(
                    id__in=deleted_new_student_ids).count()
        if model == 'Group':
            from group.models import Group
            if type_name == 'groups':
                branch_data['count'] = Group.objects.filter(branch_id=branch.id, deleted=False).count()
                branch_data['deleted_count'] = Group.objects.filter(branch_id=branch.id, deleted=True).count()
        if model == 'Teacher':
            from teachers.models import Teacher
            if type_name == 'teachers':
                branch_data['count'] = Teacher.objects.filter(user__branch_id=branch.id, deleted=False).count()
                branch_data['deleted_count'] = Teacher.objects.filter(user__branch_id=branch.id, deleted=True).count()
        if model == 'Users':
            from user.models import CustomAutoGroup
            if type_name == 'worker':
                branch_data['count'] = CustomAutoGroup.objects.filter(user__branch_id=branch.id, deleted=False).count()
                branch_data['deleted_count'] = CustomAutoGroup.objects.filter(user__branch_id=branch.id,
                                                                              deleted=True).count()
        if model == 'Rooms':
            from rooms.models import Room
            if type_name == 'rooms':
                branch_data['count'] = Room.objects.filter(branch_id=branch.id, deleted=False).count()
                branch_data['deleted_count'] = Room.objects.filter(branch_id=branch.id, deleted=True).count()
        if model == "Lead":
            from lead.models import Lead
            branch_data['count'] = Lead.objects.filter(branch_id=branch.id, deleted=False).count()
            branch_data['deleted_count'] = Lead.objects.filter(branch_id=branch.id, deleted=True).count()
        from django.db.models import Sum

        if model == 'Accounting':
            from encashment.views import OldCapital, Overhead, UserSalaryList, StudentPayment, TeacherSalaryList

            if type_name == 'capital':
                branch_data['count'] = OldCapital.objects.filter(branch_id=branch.id, deleted=False).count()
                branch_data['summa'] = \
                    OldCapital.objects.filter(branch_id=branch.id, deleted=False).aggregate(total=Sum('price'))[
                        'total'] or 0

            if type_name == 'overhead':
                branch_data['count'] = Overhead.objects.filter(branch_id=branch.id, deleted=False).count()
                branch_data['summa'] = \
                    Overhead.objects.filter(branch_id=branch.id, deleted=False).aggregate(total=Sum('price'))[
                        'total'] or 0

            if type_name == 'employeesSalary':
                branch_data['count'] = UserSalaryList.objects.filter(branch_id=branch.id, deleted=False).count()
                branch_data['summa'] = \
                    UserSalaryList.objects.filter(branch_id=branch.id, deleted=False).aggregate(total=Sum('salary'))[
                        'total'] or 0

            if type_name == 'studentsPayments':
                branch_data['count'] = StudentPayment.objects.filter(branch_id=branch.id, deleted=False,
                                                                     status=False).count()
                branch_data['summa'] = \
                    StudentPayment.objects.filter(branch_id=branch.id, deleted=False, status=False).aggregate(
                        total=Sum('payment_sum'))['total'] or 0

            if type_name == 'teachersSalary':
                branch_data['count'] = TeacherSalaryList.objects.filter(branch_id=branch.id, deleted=False).count()
                branch_data['summa'] = \
                    TeacherSalaryList.objects.filter(branch_id=branch.id, deleted=False).aggregate(total=Sum('salary'))[
                        'total'] or 0


class IsAdminOrIsSelf(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if obj == request.user:
            return True
        if request.user.has_perm(f'{obj._meta.app_label}.view_{obj._meta.model_name}'):
            return True

        return False


class IsSmm(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if request.user.groups.filter(name='Smm').exists():
            return True

        if request.user.has_perm(f'{obj._meta.app_label}.view_{obj._meta.model_name}'):
            return True

        return False


from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class CustomPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100

    def get_paginated_response(self, data):
        return Response({'count': self.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'limit': self.limit,
            'offset': self.offset,
            'results': data })
