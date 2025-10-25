from collections import defaultdict
from datetime import datetime

from django.db.models import Q
from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.core.exceptions import ValidationError
from datetime import datetime

from attendances.models import AttendancePerMonth
from books.models import BranchPayment
from books.serializers import BranchPaymentListSerializers
from capital.models import Capital
from capital.serializer.old_capital import OldCapitalsListSerializers
from capital.serializers import OldCapital
from classes.models import ClassNumber
from group.models import Group
from overhead.models import Overhead
from overhead.serializers import OverheadSerializerGet
from payments.models import PaymentTypes
from students.models import Student, DeletedStudent, DeletedNewStudent
from students.models import StudentPayment
from students.serializers import StudentPaymentSerializer
from teachers.models import TeacherSalaryList, TeacherSalary
from teachers.serializers import TeacherSalaryListCreateSerializers
from user.models import UserSalaryList, UserSalary
from user.serializers import UserSalaryListSerializers
from .models import Encashment
from lead.models import Lead
from django.db.models import Exists, OuterRef, Subquery
from django.db.models import Case, When, IntegerField, F
from django.db.models.functions import Cast
from datetime import date


class Encashments(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            ot = request.data.get('ot')
            do = request.data.get('do')
            payment_type = request.data.get('payment_type')
            branch = request.data.get('branch')

            if not all([ot, do, payment_type, branch]):
                return Response({'error': 'Missing required parameters'}, status=400)

            student_payments = StudentPayment.objects.filter(
                date__range=(ot, do),
                payment_type_id=payment_type,
                student__user__branch_id=branch,
                deleted=False,
                status=False
            ).order_by('-date')
            student_total_payment = student_payments.aggregate(total=Sum('payment_sum'))['total'] or 0
            student_serializer = StudentPaymentSerializer(student_payments.distinct(), many=True)

            teacher_salaries = TeacherSalaryList.objects.filter(
                date__range=(ot, do),
                payment_id=payment_type,
                branch_id=branch,
                deleted=False

            )
            teacher_total_salary = teacher_salaries.aggregate(total=Sum('salary'))['total'] or 0
            teacher_serializer = TeacherSalaryListCreateSerializers(teacher_salaries.distinct(), many=True)

            worker_salaries = UserSalaryList.objects.filter(
                date__range=(ot, do),
                payment_types_id=payment_type,
                branch_id=branch,
                deleted=False

            )
            worker_total_salary = worker_salaries.aggregate(total=Sum('salary'))['total'] or 0
            worker_serializer = UserSalaryListSerializers(worker_salaries.distinct(), many=True)

            branch_payments = BranchPayment.objects.filter(
                book_order__day__range=(ot, do),
                payment_type_id=payment_type,
                branch_id=branch
            )
            branch_total_payment = branch_payments.aggregate(total=Sum('payment_sum'))['total'] or 0
            branch_serializer = BranchPaymentListSerializers(branch_payments.distinct(), many=True)

            total_overhead_payment = Overhead.objects.filter(
                created__range=(ot, do),
                payment_id=payment_type,
                branch_id=branch,
                deleted=False
            ).aggregate(total=Sum('price'))['total'] or 0
            overheads = Overhead.objects.filter(
                created__range=(ot, do),
                payment_id=payment_type,
                branch_id=branch,
                deleted=False

            )
            overhead_serializer = OverheadSerializerGet(overheads, many=True)

            # total_capital = Capital.objects.filter(
            #     added_date__range=(ot, do),
            #     payment_type_id=payment_type,
            #     branch_id=branch,
            #     deleted=False
            #
            # ).aggregate(total=Sum('price'))['total'] or 0
            # capitals = Capital.objects.filter(
            #     added_date__range=(ot, do),
            #     payment_type_id=payment_type,
            #     branch_id=branch,
            #     deleted=False
            #
            # ).distinct()
            # capital_serializer = CapitalSerializers(capitals, many=True)
            total_capital = OldCapital.objects.filter(
                added_date__range=(ot, do),
                payment_type_id=payment_type,
                branch_id=branch,
                deleted=False

            ).aggregate(total=Sum('price'))['total'] or 0
            capitals = OldCapital.objects.filter(
                added_date__range=(ot, do),
                payment_type_id=payment_type,
                branch_id=branch,
                deleted=False

            ).distinct()
            capital_serializer = OldCapitalsListSerializers(capitals, many=True)
            Encashment.objects.get_or_create(
                ot=ot,
                do=do,
                payment_type_id=payment_type,
                branch_id=branch,
                total_teacher_salary=teacher_total_salary,
                total_student_payment=student_total_payment,
                total_staff_salary=worker_total_salary,
                total_branch_payment=branch_total_payment,
                total_overhead=total_overhead_payment,
                total_capital=total_capital

            )
            return Response({
                'students': {
                    'student_data': student_serializer.data,
                    'student_total_payment': student_total_payment,
                },
                'teachers': {
                    'teacher_data': teacher_serializer.data,
                    'teacher_total_salary': teacher_total_salary,
                },
                'workers': {
                    'worker_data': worker_serializer.data,
                    'worker_total_salary': worker_total_salary,
                },
                'branch': {
                    'branch_data': branch_serializer.data,
                    'branch_total_payment': branch_total_payment,
                },
                'overheads': {
                    'overhead_data': overhead_serializer.data,
                    'total_overhead_payment': total_overhead_payment,
                },
                'capitals': {
                    'capital_data': capital_serializer.data,
                    'total_capital': total_capital,
                },
                'overall': student_total_payment - (
                        teacher_total_salary + worker_total_salary + total_capital + total_overhead_payment)
            })

        except KeyError as e:
            return Response({'error': f'Missing required parameter: {str(e)}'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def get(self, request, pk):
        current_month = datetime.now().month
        current_year = datetime.now().year
        ot = datetime(current_year, current_month, 1)
        do = datetime(current_year, current_month, datetime.now().day)

        try:
            payment_types = PaymentTypes.objects.all()
            branch = pk

            all_payment_data = []

            for payment_type in payment_types:
                student_payments = StudentPayment.objects.filter(
                    added_data__range=(ot, do),
                    payment_type=payment_type,
                    student__user__branch_id=branch,
                    deleted=False,
                    status=False
                )
                student_total_payment = student_payments.aggregate(total=Sum('payment_sum'))['total'] or 0

                teacher_salaries = TeacherSalaryList.objects.filter(
                    date__range=(ot, do),
                    payment=payment_type,
                    branch_id=branch,
                    deleted=False
                )
                teacher_total_salary = teacher_salaries.aggregate(total=Sum('salary'))['total'] or 0

                worker_salaries = UserSalaryList.objects.filter(
                    date__range=(ot, do),
                    payment_types=payment_type,
                    branch_id=branch,
                    deleted=False
                )
                worker_total_salary = worker_salaries.aggregate(total=Sum('salary'))['total'] or 0

                branch_payments = BranchPayment.objects.filter(
                    book_order__day__range=(ot, do),
                    payment_type=payment_type,
                    branch_id=branch,
                )
                branch_total_payment = branch_payments.aggregate(total=Sum('payment_sum'))['total'] or 0

                total_overhead_payment = Overhead.objects.filter(
                    created__range=(ot, do),
                    payment=payment_type,
                    branch_id=branch,
                    deleted=False
                ).aggregate(total=Sum('price'))['total'] or 0

                total_capital = Capital.objects.filter(
                    added_date__range=(ot, do),
                    payment_type=payment_type,
                    branch_id=branch,
                    deleted=False

                ).aggregate(total=Sum('price'))['total'] or 0

                payment_data = {
                    'payment_type': payment_type.name,

                    'overall': student_total_payment - (
                            teacher_total_salary + worker_total_salary + branch_total_payment + total_capital + total_overhead_payment)
                }

                all_payment_data.append(payment_data)

            return Response({
                'payments': all_payment_data,
            })

        except KeyError as e:
            return Response({'error': f'Missing required parameter: {str(e)}'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class GetSchoolStudents(APIView):

    def get_class_data(self, students_list, year=None, month=None):
        total_sum_test = 0
        total_debt = 0
        reaming_debt = 0
        total_dis = 0
        total_discount = 0

        data = {
            'class': [],
            'dates': []
        }
        current_year = year if year else datetime.now().year
        current_month = month if month else datetime.now().month
        classes = (
            Group.objects
            .filter(deleted=False)
            .filter(
                Q(students__in=students_list) |  # active link
                Q(deleted_student_group__student__in=students_list)  # deleted link via DeletedStudent
                # If you only want deletions in a period/branch, add:
                # Q(deleted_student_group__student__in=students_list,
                #   deleted_student_group__deleted_date__gte=start,
                #   deleted_student_group__deleted_date__lt=end,
                #   branch_id=branch_id)
            )
            .select_related('class_number')
            .distinct()
            .order_by(
                Case(
                    When(class_number__number=0, then=0),
                    When(class_number__number__isnull=True, then=2),
                    default=1,
                    output_field=IntegerField(),
                ),
                F('class_number__number').asc(nulls_last=True),
                'id'
            )
        )
        for _class in classes:
            class_data = {
                'class_number': _class.class_number.number,
                'students': []
            }
            data['class'].append(class_data)
            class_students = (
                Student.objects
                .filter(
                    Q(groups_student=_class, groups_student__deleted=False) |
                    Q(deleted_student_student__group=_class)
                )
                # keep within your outer scope of students_list
                .filter(id__in=students_list.values('id'))
                .distinct()
            )
            for student in class_students:
                attendance_data = (
                    AttendancePerMonth.objects.filter(
                        student=student,
                        month_date__year=current_year,
                        month_date__month=current_month,
                        group=_class,
                        group__deleted=False,
                    )
                    .first()
                )
                cash_payment = 0
                bank_payment = 0
                click_payment = 0
                if attendance_data:
                    student_payments = StudentPayment.objects.filter(
                        student=student,
                        attendance=attendance_data,
                    )
                    for payment in student_payments:
                        if payment.payment_type.name == 'cash':
                            cash_payment += payment.payment_sum
                        elif payment.payment_type.name == 'bank':
                            bank_payment += payment.payment_sum
                        elif payment.payment_type.name == 'click':
                            click_payment += payment.payment_sum
                total_debt_student = attendance_data.total_debt if attendance_data else 0
                remaining_debt_student = attendance_data.remaining_debt if attendance_data else 0
                discount = getattr(attendance_data, 'discount', 0)
                paid_amount = (
                        StudentPayment.objects.filter(
                            student=student,
                            deleted=False,
                            status=True,
                            date__month=current_month,
                            date__year=current_year
                        ).aggregate(total=Sum('payment_sum'))['total'] or 0
                )
                total_debt += total_debt_student
                total_sum_test += cash_payment + bank_payment + click_payment
                reaming_debt += remaining_debt_student
                total_dis += discount
                total_discount += paid_amount
                class_data['students'].append({
                    'id': student.user.id,
                    'name': student.user.name,
                    'surname': student.user.surname,
                    'phone': student.user.phone,
                    'total_debt': total_debt_student,
                    'remaining_debt': remaining_debt_student,
                    'cash': cash_payment,
                    'bank': bank_payment,
                    'click': click_payment,
                    'total_dis': discount,
                    'total_discount': paid_amount,
                    'month_id': attendance_data.id if attendance_data else None,
                })
        unique_dates = (
            AttendancePerMonth.objects.annotate(
                year=ExtractYear('month_date'),
                month=ExtractMonth('month_date')
            )
            .filter(system__name='school')
            .values('year', 'month')
            .distinct()
            .order_by('year', 'month')
        )
        year_month_dict = defaultdict(list)
        for date in unique_dates:
            year_month_dict[date['year']].append(date['month'])
        data['dates'] = [
            {'year': year, 'months': months} for year, months in year_month_dict.items()
        ]
        data['total_sum'] = total_sum_test
        data['total_debt'] = total_debt
        data['reaming_debt'] = reaming_debt
        data['total_dis'] = total_dis
        data['total_discount'] = total_discount
        return data

    def get(self, request, *args, **kwargs):
        branch = request.query_params.get('branch')
        students_list = Student.objects.filter(user__branch_id=branch, groups_student__deleted=False,
                                               # groups_student__price__isnull=False,
                                               deleted_student_student_new__isnull=True,
                                               # deleted_student_student__isnull=True
                                               ).all()
        data = self.get_class_data(students_list)
        return Response(data)

    def post(self, request, *args, **kwargs):
        month = int(request.data.get('month'))  # e.g. 10
        year = int(request.data.get('year'))  # e.g. 2025
        branch_id = request.query_params.get('branch')

        start = date(year, month, 1)
        end = date(year + (month == 12), (month % 12) + 1, 1)  # first day of next month
        # 1) rows that are ACTIVE now in this branch
        active_in_branch = Group.objects.filter(
            students=OuterRef('pk'),
            deleted=False,
            branch_id=branch_id,
        )

        deleted_on_or_before_start = DeletedStudent.objects.filter(
            student=OuterRef('pk'),
            group__branch_id=branch_id,
            deleted_date__month__lte=month,  # <= 2025-10-01
        )

        students_list = (
            Student.objects
            .annotate(
                is_active=Exists(active_in_branch),
                was_deleted=Exists(deleted_on_or_before_start),
            )
            .filter(

                Q(is_active=True)
                |
                Q(was_deleted=True)

            )
            .distinct()
        )
        data = self.get_class_data(students_list, year=year, month=month)
        return Response(data)


class GetTeacherSalary(APIView):
    def get(self, request, *args, **kwargs):
        branch = request.query_params.get('branch')
        salaries = TeacherSalary.objects.filter(month_date__month=datetime.now().month,
                                                month_date__year=datetime.now().year,
                                                teacher__user__branch__id=branch).all()
        data = {
            'salary': [],
            'dates': [],
            'branch': branch
        }
        for salary in salaries:
            datas = {
                'id': salary.id,
                'name': salary.teacher.user.name,
                'surname': salary.teacher.user.surname,
                'phone': salary.teacher.user.phone,
                'total_salary': salary.total_salary,
                'taken_salary': salary.taken_salary,
                'remaining_salary': salary.remaining_salary,
                'subject': salary.teacher.subject.name,
                'cash': TeacherSalaryList.objects.filter(salary_id=salary.id, payment__name='cash').aggregate(
                    total=Sum('salary'))['total'] or 0,
                'bank': TeacherSalaryList.objects.filter(salary_id=salary.id, payment__name='bank').aggregate(
                    total=Sum('salary'))['total'] or 0,
                'click': TeacherSalaryList.objects.filter(salary_id=salary.id, payment__name='click').aggregate(
                    total=Sum('salary'))['total'] or 0,

            }
            data['salary'].append(datas)
        unique_dates = TeacherSalary.objects.annotate(
            year=ExtractYear('month_date'),
            month=ExtractMonth('month_date')
        ).filter(teacher__user__branch=branch).values('year', 'month').distinct().order_by('year', 'month')

        year_month_dict = {}
        for date in unique_dates:
            year = date['year']
            month = date['month']
            if year not in year_month_dict:
                year_month_dict[year] = []
            year_month_dict[year].append(month)

        data['dates'] = [{'year': year, 'months': months} for year, months in year_month_dict.items()]

        return Response(data)

    def post(self, request, *args, **kwargs):
        month = request.data.get('month')
        year = request.data.get('year')
        branch = request.query_params.get('branch')
        salaries = TeacherSalary.objects.filter(month_date__month=month,
                                                month_date__year=year, branch_id=branch).all()
        data = {
            'salary': [],
            'dates': [],
        }
        for salary in salaries:
            datas = {
                'id': salary.id,
                'name': salary.teacher.user.name,
                'surname': salary.teacher.user.surname,
                'phone': salary.teacher.user.phone,
                'total_salary': salary.total_salary,
                'taken_salary': salary.taken_salary,
                'remaining_salary': salary.remaining_salary,
                'subject': salary.teacher.subject.name,
                'cash': TeacherSalaryList.objects.filter(salary_id=salary.id, payment__name='cash').aggregate(
                    total=Sum('salary'))['total'] or 0,
                'bank': TeacherSalaryList.objects.filter(salary_id=salary.id, payment__name='bank').aggregate(
                    total=Sum('salary'))['total'] or 0,
                'click': TeacherSalaryList.objects.filter(salary_id=salary.id, payment__name='click').aggregate(
                    total=Sum('salary'))['total'] or 0,
            }
            data['salary'].append(datas)
        unique_dates = TeacherSalary.objects.annotate(
            year=ExtractYear('month_date'),
            month=ExtractMonth('month_date')
        ).filter(branch__location__system__name='school').values('year', 'month').distinct().order_by('year', 'month')

        year_month_dict = {}
        for date in unique_dates:
            year = date['year']
            month = date['month']
            if year not in year_month_dict:
                year_month_dict[year] = []
            year_month_dict[year].append(month)

        data['dates'] = [{'year': year, 'months': months} for year, months in year_month_dict.items()]

        return Response(data)


class GetEMployerSalary(APIView):
    def get(self, request, *args, **kwargs):
        branch = request.query_params.get('branch')
        salaries = UserSalary.objects.filter(date__month=datetime.now().month,
                                             date__year=datetime.now().year, user__branch__id=branch).all()
        data = {
            'salary': [],
            'dates': []
        }
        for salary in salaries:
            datas = {
                'id': salary.id,
                'name': salary.user.name,
                'surname': salary.user.surname,
                'phone': salary.user.phone,
                'total_salary': salary.total_salary,
                'taken_salary': salary.taken_salary,
                'remaining_salary': salary.remaining_salary,
                'cash': UserSalaryList.objects.filter(user_salary_id=salary.id, payment_types__name='cash').aggregate(
                    total=Sum('salary'))['total'] or 0,
                'bank': UserSalaryList.objects.filter(user_salary_id=salary.id, payment_types__name='bank').aggregate(
                    total=Sum('salary'))['total'] or 0,
                'click': UserSalaryList.objects.filter(user_salary_id=salary.id, payment_types__name='click').aggregate(
                    total=Sum('salary'))['total'] or 0,

            }
            data['salary'].append(datas)
        unique_dates = UserSalary.objects.annotate(
            year=ExtractYear('date'),
            month=ExtractMonth('date')
        ).filter(user__branch__location__system__name='school').values('year', 'month').distinct().order_by('year',
                                                                                                            'month')

        year_month_dict = {}
        for date in unique_dates:
            year = date['year']
            month = date['month']
            if year not in year_month_dict:
                year_month_dict[year] = []
            year_month_dict[year].append(month)

        data['dates'] = [{'year': year, 'months': months} for year, months in year_month_dict.items()]

        return Response(data)

    def post(self, request, *args, **kwargs):
        month = request.data.get('month')
        year = request.data.get('year')
        branch = request.query_params.get('branch')
        salaries = UserSalary.objects.filter(date__month=month,
                                             date__year=year, user__branch__id=branch).all()
        data = {
            'salary': [],
            'dates': []
        }
        for salary in salaries:
            datas = {
                'id': salary.id,
                'name': salary.user.name,
                'surname': salary.user.surname,
                'phone': salary.user.phone,
                'total_salary': salary.total_salary,
                'taken_salary': salary.taken_salary,
                'remaining_salary': salary.remaining_salary,
                'cash': UserSalaryList.objects.filter(user_salary_id=salary.id, payment_types__name='cash').aggregate(
                    total=Sum('salary'))['total'] or 0,
                'bank': UserSalaryList.objects.filter(user_salary_id=salary.id, payment_types__name='bank').aggregate(
                    total=Sum('salary'))['total'] or 0,
                'click': UserSalaryList.objects.filter(user_salary_id=salary.id, payment_types__name='click').aggregate(
                    total=Sum('salary'))['total'] or 0,
            }
            data['salary'].append(datas)
        unique_dates = UserSalary.objects.annotate(
            year=ExtractYear('date'),
            month=ExtractMonth('date')
        ).filter(user__branch__location__system__name='school').values('year', 'month').distinct().order_by('year',
                                                                                                            'month')

        year_month_dict = {}
        for date in unique_dates:
            year = date['year']
            month = date['month']
            if year not in year_month_dict:
                year_month_dict[year] = []
            year_month_dict[year].append(month)

        data['dates'] = [{'year': year, 'months': months} for year, months in year_month_dict.items()]

        return Response(data)


class EncashmentsSchool(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        ot = int(request.data.get('year', datetime.now().year))
        do = int(request.data.get('month', datetime.now().month))
        branch = request.data.get('branch')

        if not branch:
            return Response({'error': 'Missing required parameters'}, status=400)

        payment_types = PaymentTypes.objects.all()
        if not payment_types.exists():
            return Response({'error': 'Missing payment types'}, status=400)

        overall_total = 0
        payment_results = []

        attendance_per_months = AttendancePerMonth.objects.filter(
            student__user__branch_id=branch,
            month_date=datetime(ot, do, 1)
        )

        remaining_debt_total = attendance_per_months.aggregate(total=Sum('remaining_debt'))['total'] or 0
        total_debt = attendance_per_months.aggregate(total=Sum('total_debt'))['total'] or 0

        teacher_salary = TeacherSalary.objects.filter(
            month_date__month=do,
            month_date__year=ot,
            branch_id=branch
        )
        teacher_remaining_salary = teacher_salary.aggregate(total=Sum('remaining_salary'))['total'] or 0
        teacher_total_salary = teacher_salary.aggregate(total=Sum('total_salary'))['total'] or 0

        user_salary = UserSalary.objects.filter(
            date__month=do,
            date__year=ot,
            user__branch_id=branch
        )
        user_remaining_salary = user_salary.aggregate(total=Sum('remaining_salary'))['total'] or 0
        user_total_salary = user_salary.aggregate(total=Sum('total_salary'))['total'] or 0

        info = {
            "student": {
                "remaining_debt": remaining_debt_total,
                "total_debt": total_debt,
                "payments": []
            },
            "teacher": {
                "remaining_salary": teacher_remaining_salary,
                "total_salary": teacher_total_salary,
                "salaries": []
            },
            "user": {
                "remaining_salary": user_remaining_salary,
                "total_salary": user_total_salary,
                "salaries": []
            },
            "overhead": [],
            "capital": [],
            "total": []
        }

        for payment_type in payment_types:
            students_qs = AttendancePerMonth.objects.filter(
                student__user__branch_id=branch,
                month_date__year=ot,
                month_date__month=do
            )

            teachers_qs = TeacherSalary.objects.filter(
                branch_id=branch,
                month_date__year=ot,
                month_date__month=do
            )

            workers_qs = UserSalary.objects.filter(
                user__branch_id=branch,
                date__year=ot,
                date__month=do
            )

            branch_payments_qs = BranchPayment.objects.filter(
                book_order__day__year=ot,
                book_order__day__month=do,
                payment_type=payment_type,
                branch_id=branch
            )

            overhead_types = ['Gaz', 'Svet', 'Suv', 'Arenda', 'Oshxona uchun', 'Reklama uchun', 'Boshqa']
            overhead_totals = {
                name.lower().replace(' ', '_'): Overhead.objects.filter(
                    created__year=ot,
                    created__month=do,
                    payment=payment_type,
                    branch_id=branch,
                    deleted=False,
                    type__name=name
                ).aggregate(total=Sum('price'))['total'] or 0
                for name in overhead_types
            }

            total_overhead_payment = sum(overhead_totals.values())

            capital_total = OldCapital.objects.filter(
                added_date__year=ot,
                added_date__month=do,
                payment_type=payment_type,
                branch_id=branch,
                deleted=False
            ).aggregate(total=Sum('price'))['total'] or 0

            student_total_debt = students_qs.aggregate(total=Sum('total_debt'))['total'] or 0
            student_remaining = students_qs.aggregate(total=Sum('remaining_debt'))['total'] or 0
            student_payment = students_qs.aggregate(total=Sum('payment'))['total'] or 0

            teacher_total_salary = teachers_qs.aggregate(total=Sum('total_salary'))['total'] or 0
            teacher_remaining_salary = teachers_qs.aggregate(total=Sum('remaining_salary'))['total'] or 0
            teacher_taken_salary = teachers_qs.aggregate(total=Sum('taken_salary'))['total'] or 0

            worker_total_salary = workers_qs.aggregate(total=Sum('total_salary'))['total'] or 0
            worker_remaining_salary = workers_qs.aggregate(total=Sum('remaining_salary'))['total'] or 0
            worker_taken_salary = workers_qs.aggregate(total=Sum('taken_salary'))['total'] or 0

            branch_total_payment = branch_payments_qs.aggregate(total=Sum('payment_sum'))['total'] or 0

            payment_total = student_payment - (
                    teacher_total_salary + worker_taken_salary + capital_total + total_overhead_payment
            )
            overall_total += payment_total

            # Build the full report per payment type
            payment_results.append({
                'payment_type': payment_type.name,
                'students': {
                    'student_total_payment': student_payment,
                    'total_debt': student_total_debt,
                    'remaining_debt': student_remaining
                },
                'teachers': {
                    'taken': teacher_taken_salary,
                    'remaining_salary': teacher_remaining_salary,
                    'total_salary': teacher_total_salary
                },
                'workers': {
                    'taken': worker_taken_salary,
                    'remaining_salary': worker_remaining_salary,
                    'total_salary': worker_total_salary
                },
                'branch': {
                    'branch_total_payment': branch_total_payment
                },
                'overheads': {
                    'total_overhead_payment': total_overhead_payment,
                    **overhead_totals
                },
                'capitals': {
                    'total_capital': capital_total
                },
                'payment_total': payment_total
            })

            # Optional: Populate the summary info dictionary
            info['student']['payments'].append({
                "payment_type": payment_type.name,
                "student_total_payment": student_payment
            })
            info['teacher']['salaries'].append({
                "payment_type": payment_type.name,
                "teacher_total_salary": teacher_total_salary
            })
            info['user']['salaries'].append({
                "payment_type": payment_type.name,
                "worker_total_salary": worker_total_salary
            })
            info['overhead'].append({
                "payment_type": payment_type.name,
                "total_overhead_payment": total_overhead_payment
            })
            info['capital'].append({
                "payment_type": payment_type.name,
                "total_capital": capital_total
            })
            info['total'].append({
                "payment_type": payment_type.name,
                "payment_total": payment_total
            })

        # Unique dates for frontend filtering
        unique_dates = UserSalary.objects.annotate(
            year=ExtractYear('date'),
            month=ExtractMonth('date')
        ).filter(
            user__branch__location__system__name='school'
        ).values('year', 'month').distinct().order_by('year', 'month')

        year_month_dict = {}
        for date in unique_dates:
            year = date['year']
            month = date['month']
            if year not in year_month_dict:
                year_month_dict[year] = []
            year_month_dict[year].append(month)

        return Response({
            'payment_results': payment_results,
            'summary': info,
            'overall_total': overall_total,
            'dates': [{'year': year, 'months': months} for year, months in year_month_dict.items()],
        })


from django.db.models import Sum, Prefetch, Q

from django.db.models import Sum, F, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError


class OneDayReportView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            validated_data = self._validate_request_data(request.data)
            payment_type = request.query_params.get("payment_type")

            report_data = self._generate_report_data(
                from_date=validated_data['from_date'],
                to_date=validated_data['to_date'],
                branch_id=validated_data['branch'],
                payment_type=payment_type
            )

            return Response(report_data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # except Exception:
        #     return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _validate_request_data(self, data):
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        branch = data.get('branch')

        if not all([from_date, to_date, branch]):
            raise ValidationError("from_date, to_date, and branch are required")

        return {
            'from_date': from_date,
            'to_date': to_date,
            'branch': branch
        }

    def _generate_report_data(self, from_date, to_date, branch_id, payment_type=None):
        return {
            "student_payments": self._get_student_payments_data(from_date, to_date, branch_id, payment_type),
            "teacher_salaries": self._get_teacher_salaries_data(from_date, to_date, branch_id, payment_type),
            "user_salaries": self._get_user_salaries_data(from_date, to_date, branch_id, payment_type),
            "overhead_payments": self._get_overhead_payments_data(from_date, to_date, branch_id, payment_type),
            "new_students": self._get_new_students_data(from_date, to_date, branch_id),
            "new_studying_students": self._get_new_studying_students_data(from_date, to_date, branch_id),
            "new_leads": self._get_new_leads_data(from_date, to_date, branch_id),
        }

    def _get_report_data(self, qs, fields, sum_field):
        """
        qs -> QuerySet
        fields -> dict {alias: field_lookup}
        sum_field -> str (umumiy summani olish uchun)
        """
        total = qs.aggregate(total=Sum(sum_field))["total"] or 0
        data = list(qs.values(**fields))
        return {"count": qs.count(), "total": total, "data": data}

    def _get_student_payments_data(self, from_date, to_date, branch_id, payment_type=None):
        qs = StudentPayment.objects.filter(
            added_data__range=(from_date, to_date),
            branch_id=branch_id,
            deleted=False
        ).select_related("student__user", "payment_type")

        if payment_type:
            qs = qs.filter(payment_type__name=payment_type)

        fields = {
            "name": F("student__user__name"),
            "surname": F("student__user__surname"),
            "payment": F("payment_type__name"),
            "payment_sum1": F("payment_sum"),
        }
        return self._get_report_data(qs, fields, "payment_sum")

    def _get_teacher_salaries_data(self, from_date, to_date, branch_id, payment_type=None):
        qs = TeacherSalaryList.objects.filter(
            date__range=(from_date, to_date),
            branch_id=branch_id,
            deleted=False
        ).select_related("teacher__user", "payment")

        if payment_type:
            qs = qs.filter(payment__name=payment_type)

        fields = {
            "name": F("teacher__user__name"),
            "surname": F("teacher__user__surname"),
            "salary1": F("salary"),
            "payment1": F("payment__name"),
            "comment1": F("comment"),
        }
        return self._get_report_data(qs, fields, "salary")

    def _get_user_salaries_data(self, from_date, to_date, branch_id, payment_type=None):
        qs = UserSalaryList.objects.filter(
            date__range=(from_date, to_date),
            branch_id=branch_id,
            deleted=False
        ).select_related("user", "payment_types")

        if payment_type:
            qs = qs.filter(payment_types__name=payment_type)

        fields = {
            "name": F("user__name"),
            "surname": F("user__surname"),
            "salary1": F("salary"),
            "payment": F("payment_types__name"),
            "comment1": F("comment"),
        }
        return self._get_report_data(qs, fields, "salary")

    def _get_overhead_payments_data(self, from_date, to_date, branch_id, payment_type=None):
        qs = Overhead.objects.filter(
            created__range=(from_date, to_date),
            branch_id=branch_id,
            deleted=False
        ).select_related("type", "payment")

        if payment_type:
            qs = qs.filter(payment__name=payment_type)

        fields = {
            "name1": F("name"),
            "payment1": F("payment__name"),
            "payment_sum": F("price"),
        }
        data = [
            {
                "name": item["name1"] if item["name1"] else o.type.name,
                "payment": item["payment1"],
                "payment_sum": item["payment_sum"]
            }
            for o, item in zip(qs, qs.values(**fields))
        ]

        total = qs.aggregate(total=Sum("price"))["total"] or 0
        return {"count": qs.count(), "total": total, "data": data}

    def _get_excluded_student_ids(self):
        deleted_student_ids = list(
            DeletedStudent.objects.filter(deleted=False)
            .values_list('student_id', flat=True)
        )
        deleted_new_student_ids = list(
            DeletedNewStudent.objects.values_list('student_id', flat=True)
        )
        return deleted_student_ids + deleted_new_student_ids

    def _get_new_students_data(self, from_date, to_date, branch_id):
        excluded_ids = self._get_excluded_student_ids()

        qs = Student.objects.filter(
            ~Q(id__in=excluded_ids),
            user__branch_id=branch_id,
            user__registered_date__range=(from_date, to_date),
            groups_student__isnull=True
        ).select_related('user').distinct()

        data = list(qs.values(name=F("user__name"), surname=F("user__surname")))
        return {"count": qs.count(), "data": data}

    def _get_new_studying_students_data(self, from_date, to_date, branch_id):
        deleted_student_ids = DeletedStudent.objects.filter(
            student__groups_student__isnull=True, deleted=False
        ).values_list('student_id', flat=True)

        deleted_new_student_ids = DeletedNewStudent.objects.values_list('student_id', flat=True)

        qs = Student.objects.exclude(
            id__in=deleted_student_ids
        ).exclude(
            id__in=deleted_new_student_ids
        ).filter(
            groups_student__isnull=False,
            joined_group__range=(from_date, to_date)
        ).select_related('user', 'class_number').distinct()

        data = list(qs.values(name=F("user__name"), surname=F("user__surname")))
        return {"count": qs.count(), "data": data}

    def _get_new_leads_data(self, from_date, to_date, branch_id):
        qs = Lead.objects.filter(
            created__range=(from_date, to_date),
            branch_id=branch_id,
            deleted=False
        )
        data = list(qs.values("name", "surname", "phone"))
        return {"count": qs.count(), "data": data}
