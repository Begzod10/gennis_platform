from rest_framework.views import APIView

from students.models import StudentPayment
from teachers.models import TeacherSalaryList
from user.models import UserSalaryList


class Encashment(APIView):
    def post(self, request, *args, **kwargs):
        ot = request.data['ot']
        do = request.data['do']
        payment_type = request.data['payment_type']
        student_total_payment = 0
        student_payments = StudentPayment.objects.filter(added_data__range=(ot, do), payment_type=payment_type)
        for student_payment in student_payments:
            student_total_payment += student_payment.payment_sum
        teacher_total_salary = 0
        teacher_salaries = TeacherSalaryList.objects.filter(date__range=(ot, do), payment=payment_type)
        for teacher_salary in teacher_salaries:
            teacher_total_salary += teacher_salary.salary
        worker_total_salary = 0
        worker_salaries = UserSalaryList.objects.filter(date__range=(ot, do), payment=payment_type)
        for worker_salary in worker_salaries:
            worker_total_salary += worker_salary.salary
