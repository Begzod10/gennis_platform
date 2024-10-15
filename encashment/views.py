from datetime import datetime

from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from attendances.models import AttendancePerMonth
from books.models import BranchPayment
from books.serializers import BranchPaymentListSerializers
from capital.models import Capital
from capital.serializers import OldCapital, OldCapitalListSerializers
from classes.models import ClassNumber
from overhead.models import Overhead
from overhead.serializers import OverheadSerializerGet
from payments.models import PaymentTypes
from students.models import Student
from students.models import StudentPayment
from students.serializers import StudentPaymentSerializer
from teachers.models import TeacherSalaryList, TeacherSalary
from teachers.serializers import TeacherSalaryListCreateSerializers
from user.models import UserSalaryList, UserSalary
from user.serializers import UserSalaryListSerializers
from .models import Encashment


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
            ).order_by('date')
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
            capital_serializer = OldCapitalListSerializers(capitals, many=True)
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

    def get_class_data(self, classes, year=None, month=None):
        data = {
            'class': [],
            'dates': []
        }

        current_year = year if year else datetime.now().year
        current_month = month if month else datetime.now().month

        for _class in classes:
            sinflar = {
                'class_number': _class.number,
                'students': []
            }
            data['class'].append(sinflar)

            students = Student.objects.filter(groups_student__class_number=_class)

            attendance_data = AttendancePerMonth.objects.filter(
                student__in=students,
                month_date__year=current_year,
                month_date__month=current_month
            ).select_related('student')

            student_attendance_map = {att.student.id: att for att in attendance_data}

            payment_data = StudentPayment.objects.filter(
                student_id__in=students,
                date__month=current_month,
                date__year=current_year,
                deleted=False,
                status=False

            ).values('student_id', 'payment_type__name').annotate(total_sum=Sum('payment_sum'))

            student_payment_map = {}
            for payment in payment_data:
                student_id = payment['student_id']
                payment_type = payment['payment_type__name']
                total_sum = payment['total_sum']

                if student_id not in student_payment_map:
                    student_payment_map[student_id] = {}
                student_payment_map[student_id][payment_type] = total_sum

            for student in students:
                attendance = student_attendance_map.get(student.id)

                payments = student_payment_map.get(student.id, {})
                cash_payment = payments.get('cash', 0)
                bank_payment = payments.get('bank', 0)
                click_payment = payments.get('click', 0)

                sinflar['students'].append({
                    'id': student.user.id,
                    'name': student.user.name,
                    'surname': student.user.surname,
                    'phone': student.user.phone,
                    'total_debt': attendance.total_debt if attendance else 0,
                    'remaining_debt': attendance.remaining_debt if attendance else 0,
                    'cash': cash_payment,
                    'bank': bank_payment,
                    'click': click_payment,
                })

        unique_dates = AttendancePerMonth.objects.annotate(
            year=ExtractYear('month_date'),
            month=ExtractMonth('month_date')
        ).filter(system__name='school').values('year', 'month').distinct().order_by('year', 'month')

        year_month_dict = {}
        for date in unique_dates:
            year = date['year']
            month = date['month']
            if year not in year_month_dict:
                year_month_dict[year] = []
            year_month_dict[year].append(month)

        data['dates'] = [{'year': year, 'months': months} for year, months in year_month_dict.items()]

        return data

    def get(self, request, *args, **kwargs):
        branch = request.query_params.get('branch')
        classes = ClassNumber.objects.filter(
            price__isnull=False,
            branch_id=branch
        ).order_by('number')

        data = self.get_class_data(classes)
        return Response(data)

    def post(self, request, *args, **kwargs):
        month = request.data.get('month')
        year = request.data.get('year')
        branch = request.query_params.get('branch')

        classes = ClassNumber.objects.filter(
            price__isnull=False,
            branch_id=branch
        ).order_by('number')

        data = self.get_class_data(classes, year=year, month=month)
        return Response(data)


class GetTeacherSalary(APIView):
    def get(self, request, *args, **kwargs):
        branch = request.query_params.get('branch')
        salaries = TeacherSalary.objects.filter(month_date__month=datetime.now().month,
                                                month_date__year=datetime.now().year, branch_id=branch).all()
        data = {
            'salary': [],
            'dates': []
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

    def post(self, request, *args, **kwargs):
        month = request.data.get('month')
        year = request.data.get('year')
        branch = request.query_params.get('branch')
        salaries = TeacherSalary.objects.filter(month_date__month=month,
                                                month_date__year=year, branch_id=branch).all()
        data = {}
        for salary in salaries:
            datas = {
                'id': salary.id,
                'name': salary.teacher.user.name,
                'surname': salary.teacher.user.surname,
                'phone': salary.teacher.user.phone,
                'total_salary': salary.salary,
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
        data = {}
        for salary in salaries:
            datas = {
                'id': salary.id,
                'name': salary.user.name,
                'surname': salary.user.surname,
                'phone': salary.user.phone,
                'total_salary': salary.salary,
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

        if not all([ot, do, branch]):
            return Response({'error': 'Missing required parameters'}, status=400)

        payment_types = PaymentTypes.objects.all()

        if not payment_types:
            return Response({'error': 'Missing payment types'}, status=400)

        overall_total = 0  # For storing the overall total

        payment_results = []

        for payment_type in payment_types:
            student_payments = StudentPayment.objects.filter(
                added_data__month=do,
                added_data__year=ot,
                payment_type=payment_type,
                student__user__branch_id=branch,
                deleted=False,
                status=False
            )
            student_total_payment = student_payments.aggregate(total=Sum('payment_sum'))['total'] or 0

            teacher_salaries = TeacherSalaryList.objects.filter(
                date__month=do,
                date__year=ot,
                payment=payment_type,
                branch_id=branch,
                deleted=False
            )
            teacher_total_salary = teacher_salaries.aggregate(total=Sum('salary'))['total'] or 0

            worker_salaries = UserSalaryList.objects.filter(
                date__month=do,
                date__year=ot,
                payment_types=payment_type,
                branch_id=branch,
                deleted=False
            )
            worker_total_salary = worker_salaries.aggregate(total=Sum('salary'))['total'] or 0

            branch_payments = BranchPayment.objects.filter(
                book_order__day__month=do,
                book_order__day__year=ot,
                payment_type=payment_type,
                branch_id=branch
            )
            branch_total_payment = branch_payments.aggregate(total=Sum('payment_sum'))['total'] or 0

            total_overhead_payment = Overhead.objects.filter(
                created__month=do,
                created__year=ot,
                payment=payment_type,
                branch_id=branch,
                deleted=False
            ).aggregate(total=Sum('price'))['total'] or 0

            total_capital = OldCapital.objects.filter(
                added_date__year=ot,
                added_date__month=do,
                payment_type=payment_type,
                branch_id=branch,
                deleted=False
            ).aggregate(total=Sum('price'))['total'] or 0

            payment_total = student_total_payment - (
                    teacher_total_salary + worker_total_salary + total_capital + total_overhead_payment)

            # Accumulate the overall total
            overall_total += payment_total

            payment_results.append({
                'payment_type': payment_type.name,  # Convert to a string or use payment_type.id
                'students': {'student_total_payment': student_total_payment},
                'teachers': {'teacher_total_salary': teacher_total_salary},
                'workers': {'worker_total_salary': worker_total_salary},
                'branch': {'branch_total_payment': branch_total_payment},
                'overheads': {'total_overhead_payment': total_overhead_payment},
                'capitals': {'total_capital': total_capital},
                'payment_total': payment_total
            })
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

        return Response({
            'payment_results': payment_results,
            'overall_total': overall_total,
            'dates': [{'year': year, 'months': months} for year, months in year_month_dict.items()],
        })
