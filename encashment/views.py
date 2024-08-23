from datetime import datetime

from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.views import APIView

from books.models import BranchPayment
from books.serializers import BranchPaymentListSerializers
from capital.models import Capital
from capital.serializers import CapitalSerializers
from overhead.models import Overhead
from overhead.serializers import OverheadSerializerGet
from payments.models import PaymentTypes
from students.models import StudentPayment
from students.serializers import StudentPaymentSerializer
from teachers.models import TeacherSalaryList
from teachers.serializers import TeacherSalaryListReadSerializers
from user.models import UserSalaryList
from user.serializers import UserSalaryListSerializers
from .models import Encashment


class Encashments(APIView):
    def post(self, request, *args, **kwargs):
        try:
            ot = request.data.get('ot')
            do = request.data.get('do')
            payment_type = request.data.get('payment_type')
            branch = request.data.get('branch')

            if not all([ot, do, payment_type, branch]):
                return Response({'error': 'Missing required parameters'}, status=400)

            student_payments = StudentPayment.objects.filter(
                added_data__range=(ot, do),
                payment_type_id=payment_type,
                student__user__branch_id=branch
            )
            student_total_payment = student_payments.aggregate(total=Sum('payment_sum'))['total'] or 0
            student_serializer = StudentPaymentSerializer(student_payments.distinct(), many=True)

            teacher_salaries = TeacherSalaryList.objects.filter(
                date__range=(ot, do),
                payment_id=payment_type,
                branch_id=branch
            )
            teacher_total_salary = teacher_salaries.aggregate(total=Sum('salary'))['total'] or 0
            teacher_serializer = TeacherSalaryListReadSerializers(teacher_salaries.distinct(), many=True)

            worker_salaries = UserSalaryList.objects.filter(
                date__range=(ot, do),
                payment_types_id=payment_type,
                branch_id=branch
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
                branch_id=branch
            ).aggregate(total=Sum('price'))['total'] or 0
            overheads = Overhead.objects.filter(
                created__range=(ot, do),
                payment_id=payment_type,
                branch_id=branch
            ).distinct()
            overhead_serializer = OverheadSerializerGet(overheads, many=True)

            total_capital = Capital.objects.filter(
                added_date__range=(ot, do),
                payment_type_id=payment_type,
                branch_id=branch
            ).aggregate(total=Sum('price'))['total'] or 0
            capitals = Capital.objects.filter(
                added_date__range=(ot, do),
                payment_type_id=payment_type,
                branch_id=branch
            ).distinct()
            capital_serializer = CapitalSerializers(capitals, many=True)
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
                'overall': student_total_payment - (teacher_total_salary + worker_total_salary)
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
                    payment_type_id=payment_type,
                    student__user__branch_id=branch
                )
                student_total_payment = student_payments.aggregate(total=Sum('payment_sum'))['total'] or 0
                student_serializer = StudentPaymentSerializer(student_payments.distinct(), many=True)

                teacher_salaries = TeacherSalaryList.objects.filter(
                    date__range=(ot, do),
                    payment_id=payment_type,
                    branch_id=branch
                )
                teacher_total_salary = teacher_salaries.aggregate(total=Sum('salary'))['total'] or 0
                teacher_serializer = TeacherSalaryListReadSerializers(teacher_salaries.distinct(), many=True)

                worker_salaries = UserSalaryList.objects.filter(
                    date__range=(ot, do),
                    payment_types_id=payment_type,
                    branch_id=branch
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
                    branch_id=branch
                ).aggregate(total=Sum('price'))['total'] or 0
                overheads = Overhead.objects.filter(
                    created__range=(ot, do),
                    payment_id=payment_type,
                    branch_id=branch
                ).distinct()
                overhead_serializer = OverheadSerializerGet(overheads, many=True)

                total_capital = Capital.objects.filter(
                    added_date__range=(ot, do),
                    payment_type_id=payment_type,
                    branch_id=branch
                ).aggregate(total=Sum('price'))['total'] or 0
                capitals = Capital.objects.filter(
                    added_date__range=(ot, do),
                    payment_type_id=payment_type,
                    branch_id=branch
                ).distinct()
                capital_serializer = CapitalSerializers(capitals, many=True)

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

                payment_data = {
                    'payment_type': payment_type.name,
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
