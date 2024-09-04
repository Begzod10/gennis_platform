import datetime
import json
import os
import uuid
from datetime import datetime

import docx
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from branch.models import Branch
from permissions.response import QueryParamFilterMixin
from teachers.models import TeacherBlackSalary
from .models import Student, DeletedStudent, ContractStudent, DeletedNewStudent, StudentPayment
from .serializers import StudentCharity
from .serializers import (StudentListSerializer,
                          DeletedStudentListSerializer, DeletedNewStudentListSerializer, StudentPaymentListSerializer)


class StudentListView(APIView):
    def get(self, request, *args, **kwargs):
        deleted_student_ids = DeletedStudent.objects.values_list('student_id', flat=True)
        deleted_new_student_ids = DeletedNewStudent.objects.values_list('student_id', flat=True)
        active_students = Student.objects.exclude(id__in=deleted_student_ids).exclude(id__in=deleted_new_student_ids)[
                          :100]
        student_serializer = StudentListSerializer(active_students, many=True)

        deleted_students = DeletedStudent.objects.all()
        deleted_student_serializer = DeletedStudentListSerializer(deleted_students, many=True)
        delete_new_students = DeletedNewStudent.objects.exclude(id__in=deleted_student_ids)
        delete_new_student_serializer = DeletedNewStudentListSerializer(delete_new_students, many=True)

        data = {
            'new_students': student_serializer.data,
            'deleted_students': deleted_student_serializer.data,
            'active': delete_new_student_serializer.data,
        }

        return Response(data)


class DeletedFromRegistered(QueryParamFilterMixin, APIView):
    permission_classes = [IsAuthenticated]

    filter_mappings = {
        'branch': 'student__user__branch_id',
        'subject': 'subject__id',
        'age': 'student__user__birth_date',
        'language': 'student__user__language_id',
    }

    def get(self, request, *args, **kwargs):
        deleted_student_ids = DeletedStudent.objects.values_list('student_id', flat=True)
        delete_new_students = DeletedNewStudent.objects.exclude(id__in=deleted_student_ids)

        delete_new_students = self.filter_queryset(delete_new_students)
        delete_new_student_serializer = DeletedNewStudentListSerializer(delete_new_students, many=True)
        return Response(delete_new_student_serializer.data)


class DeletedGroupStudents(QueryParamFilterMixin, APIView):
    permission_classes = [IsAuthenticated]
    filter_mappings = {
        'branch': 'user__branch_id',
        'subject': 'subject__id',
        'age': 'user__birth_date',
        'language': 'user__language_id',
    }

    def get(self, request, *args, **kwargs):
        deleted_new_student_ids = DeletedNewStudent.objects.values_list('student_id', flat=True)
        active_students = Student.objects.exclude(id__in=deleted_new_student_ids)
        active_students = self.filter_queryset(active_students)
        student_serializer = StudentListSerializer(active_students, many=True)
        return Response(student_serializer.data)


class NewRegisteredStudents(QueryParamFilterMixin, APIView):
    permission_classes = [IsAuthenticated]

    filter_mappings = {
        'branch': 'user__branch_id',
        'subject': 'subject__id',
        'age': 'user__birth_date',
        'language': 'user__language_id',
    }
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__name', 'user__surname', 'user__username']

    def get(self, request, *args, **kwargs):
        excluded_ids = list(DeletedStudent.objects.values_list('student_id', flat=True)) + \
                       list(DeletedNewStudent.objects.values_list('student_id', flat=True))

        active_students = Student.objects.select_related('user').filter(
            ~Q(id__in=excluded_ids) & Q(groups_student__isnull=True)
        ).distinct()

        filtered_students = self.filter_queryset(active_students)
        search_filter = filters.SearchFilter()
        filtered_students = search_filter.filter_queryset(request, filtered_students, self)

        student_serializer = StudentListSerializer(filtered_students, many=True)

        return Response(student_serializer.data)


class ActiveStudents(QueryParamFilterMixin, APIView):
    filter_mappings = {
        'branch': 'user__branch_id',
        'subject': 'subject__id',
        'age': 'user__birth_date',
        'language': 'user__language_id',
    }

    def get(self, request, *args, **kwasrgs):
        deleted_student_ids = DeletedStudent.objects.values_list('student_id', flat=True)
        deleted_new_student_ids = DeletedNewStudent.objects.values_list('student_id', flat=True)
        active_students = Student.objects.exclude(id__in=deleted_student_ids) \
            .exclude(id__in=deleted_new_student_ids) \
            .filter(groups_student__isnull=False).distinct()

        active_students = self.filter_queryset(active_students)

        student_serializer = StudentListSerializer(active_students, many=True)

        return Response(student_serializer.data)


class CreateContractView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        data = request.data

        calendar_year, calendar_month, calendar_day = self._get_calendar_date()
        calendar_year = str(calendar_year)  # Ensure calendar_year is a string
        student = get_object_or_404(Student, id=user_id)

        try:
            ot = datetime.strptime(data['date']['ot'], "%Y-%m-%d").date()
            do = datetime.strptime(data['date']['do'], "%Y-%m-%d").date()
        except KeyError as e:
            return Response({"error": f"Sanani aniqlashda xato: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Sanalar noto'g'ri formatda, YYYY-MM-DD formatida kiriting"},
                            status=status.HTTP_400_BAD_REQUEST)

        student.representative_name = data.get('name', student.representative_name)
        student.representative_surname = data.get('surname', student.representative_surname)
        student.save()

        ot_month, do_month = ot.month, do.month
        do_year = do.year

        if do_year > int(calendar_year):
            do_month += 12

        month = do_month - ot_month + 1
        user = student.user
        location = get_object_or_404(Branch, id=user.branch_id)
        contract = ContractStudent.objects.filter(student_id=student.id).first()
        student_charity = StudentCharity.objects.filter(student_id=student.id)
        all_charity = sum(char.charity_sum for char in student_charity)

        if contract and contract.contract and os.path.exists(contract.contract.path):
            os.remove(contract.contract.path)
            contract.contract = ""

        contract_data = ContractStudent.objects.filter(student_id=student.id, year=datetime.now()).first()

        if not contract:
            contract = ContractStudent(
                student=student,
                created_date=ot,
                expire_date=do,
                father_name=data.get('fatherName', ''),
                given_place=data.get('givenPlace', ''),
                place=data.get('place', ''),
                passport_series=data.get('passportSeries', ''),
                given_time=data.get('givenTime', ''),
                year=datetime.now()
            )
            contract.save()
            if not contract_data:
                ContractStudent(year=datetime.now(), student=student).save()
            else:
                contract_data.number += 1
                contract_data.save()
        else:
            ContractStudent.objects.filter(id=contract.id).update(
                created_date=ot,
                expire_date=do,
                father_name=data.get('fatherName', contract.father_name),
                given_place=data.get('givenPlace', contract.given_place),
                place=data.get('place', contract.place),
                passport_series=data.get('passportSeries', contract.passport_series),
                given_time=data.get('givenTime', contract.given_time)
            )

        doc = docx.Document('media/contract.docx')
        user_name, user_surname, father_name = (
            (user.name, user.surname, user.father_name) if int(user.calculate_age()) >= 18
            else (student.representative_name, student.representative_surname, contract.father_name)
        )

        id_hex = uuid.uuid1().hex[:15]
        campus_name = f"{location.name} {location.name}" if location.location_type == "Shahri" else f"{location.district} {location.location_type}"
        number = f'{calendar_year}/{location.code}/{1}'

        self._fill_doc(doc, location, contract, user, student, id_hex, campus_name, number, ot, do, month, all_charity)

        doc_path = f"media/contracts/{id_hex} {user.name.title()} {user.surname.title()}doc.docx"
        doc.save(doc_path)
        contract.contract = doc_path
        contract.save()

        return Response({"success": True, "msg": "Shartnoma muvaffaqiyatli yaratildi", "file": doc_path})

    def _get_calendar_date(self):
        now = datetime.now()
        return now.year, now.month, now.day

    def _fill_doc(self, doc, location, contract, user, student, id_hex, campus_name, number, ot, do, month,
                  all_charity):
        doc.paragraphs[0].runs[0].text = f"SHARTNOMA № {number}"
        doc.paragraphs[3].text = f"{campus_name} {ot.strftime('%d-%m-%Y')}"
        if location.id > 3:
            doc.paragraphs[
                5].text = "O‘zbekiston Respublikasi Prezidentining 15.09.2017-yildagi PQ-3276 sonli “Nodavlat taʼlim xizmatlarini yanada rivojlantirish chora-tadbirlari toʻgʻrisida”gi qaroriga."
        else:
            doc.paragraphs[5].text = ""

        doc.paragraphs[
            6].text = f"Taʼlim muassasasi, yaʼni {location.campus_name} (keyingi o‘rinlarda “Nodavlat taʼlim muassasasi” deb yuritiladi), direktor {location.director_fio} nomidan va {student.representative_surname.title()} {student.representative_name.title()} {contract.father_name[0].title()}{contract.father_name[1:].lower()} bilan bir tomondan"
        doc.paragraphs[
            9].text = f"1.1 Ushbu shartnomaga muvofiq, o‘quvchining ota-onasi (yoki qonuniy vakili) o‘zining voyaga yetmagan farzandini {user.name.title()} {user.surname.title()} {user.father_name[0].title()}{user.father_name[1:].lower()} ni qo‘shimcha taʼlim olish uchun qabul qilmoqda."
        doc.paragraphs[
            15].text = f"2.1 O‘quvchining nodavlat taʼlim muassasida taʼlim olishi uchun bir oylik to‘lov summasi {abs(student.total_payment_month) - all_charity} va {contract.expire_date.strftime('%d-%m-%Y')} muddatgacha {abs(((student.total_payment_month) - all_charity) * month)} so‘mni tashkil etadi."
        doc.paragraphs[
            69].text = f"7.1 Ushbu shartnoma tomonlar o‘rtasida imzolangan kundan boshlab yuridik kuchga ega bo‘ladi va {contract.expire_date.strftime('%d-%m-%Y')} muddatga qadar amal qiladi."

        info = [
            {"left_info": f"{location.campus_name} NTM",
             "right_info": f"F.I.O: {student.representative_surname.title()} {student.representative_name.title()} {contract.father_name[0].title()}{contract.father_name[1:].lower()}"},
            {"left_info": location.address, "right_info": f"Pasport maʼlumotlari: Seriya {contract.passport_series}"},
            {"left_info": f"R/S: {location.bank_sheet}  INN: {location.inn}",
             "right_info": f"Berilgan vaqti: {contract.given_time}"},
            {"left_info": f"Bank: {location.bank}", "right_info": f"Manzil: {contract.place}"},
            {"left_info": f"MFO: {location.mfo}", "right_info": ""},
            {"left_info": f"Tel: {location.number}", "right_info": ""},
            {"left_info": f"Direktor: __________{location.director_fio}", "right_info": ""},
            {"left_info": "M.P", "right_info": "Imzo____________"}
        ]

        table = doc.add_table(rows=1, cols=2)
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Nodavlat taʼlim muassasasi'
        hdr_cells[1].text = 'O‘quvchining qonuniy vakili (ota-onasi)'

        for item in info:
            row_cells = table.add_row().cells
            row_cells[0].text = item['left_info']
            row_cells[1].text = item['right_info']


class UploadPDFContractView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        student = get_object_or_404(ContractStudent, student__id=user_id)
        file = request.FILES.get('file')
        student.contract = file
        student.save()

        return Response({"success": True, "msg": "File uploaded successfully", "url": str(student.contract)})


class PaymentDatas(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, student_id):
        data = json.loads(request.body)
        year = data['year']
        month = data['month']
        payments = StudentPayment.objects.filter(deleted=False, student_id=student_id, added_data__year=year,
                                                 added_data__month=month).all()
        data = StudentPaymentListSerializer(payments, many=True).data

        return Response(data)

    def get(self, request, student_id):

        student_payments = StudentPayment.objects.filter(deleted=False, student_id=student_id).all()

        payments_by_year = {}

        for payment in student_payments:
            year = payment.added_data.year
            month = payment.added_data.month

            if year not in payments_by_year:
                payments_by_year[year] = set()
            payments_by_year[year].add(month)

        payments_by_year_list = [
            {'name': year, 'months': sorted(months)}
            for year, months in payments_by_year.items()
        ]

        return Response({
            'payments_by_year': payments_by_year_list,
        })


class GetMonth(APIView):

    def get(self, request, student_id, attendance_id):
        from attendances.models import AttendancePerMonth
        month = AttendancePerMonth.objects.exclude(total_debt=0).filter(student_id=student_id, status=False).all()
        data = []
        for mont in month:
            if isinstance(mont.month_date, str):
                month_date = datetime.strptime(mont.month_date, "%Y-%m-%d")
            else:
                month_date = mont.month_date
            month_name = month_date.strftime("%B")
            month_number = month_date.strftime("%m")
            if mont.total_debt != mont.payment and mont.remaining_debt == 0:
                mont.remaining_debt = mont.total_debt
                mont.save()
            data.append(
                {
                    'id': mont.id,
                    'name': month_name,
                    'number': month_number,
                    'price': mont.remaining_debt
                }
            )
        return Response(data)

    def post(self, request, student_id, attendance_id):
        from attendances.models import AttendancePerMonth
        attendance_per_months = AttendancePerMonth.objects.get(pk=attendance_id)
        if attendance_per_months.total_debt != attendance_per_months.payment and attendance_per_months.remaining_debt == 0:
            attendance_per_months.remaining_debt = attendance_per_months.total_debt
            attendance_per_months.save()
        student = Student.objects.get(pk=student_id)
        data = json.loads(request.body)
        payment_sum = data['payment_sum']
        branch = data['branch']
        student_payment = StudentPayment.objects.create(student=student, payment_sum=payment_sum, branch=branch)
        if student_payment.extra_payment:
            payment_sum = student_payment.payment_sum + student_payment.extra_payment
        else:
            payment_sum = 0

        for attendance_per_month in attendance_per_months:
            if attendance_per_month.remaining_debt >= payment_sum:
                attendance_per_month.remaining_debt -= payment_sum
                attendance_per_month.payment += payment_sum
                payment_sum = 0
                if attendance_per_month.remaining_debt == 0:
                    attendance_per_month.status = True
            else:
                payment_sum -= attendance_per_month.remaining_debt
                attendance_per_month.payment += attendance_per_month.remaining_debt
                attendance_per_month.remaining_debt = 0
                attendance_per_month.status = True
            attendance_per_month.save()

        student_payment.extra_payment = payment_sum
        student_payment.save()

        total_debt = 0
        remaining_debt = 0
        attendance_per_months = AttendancePerMonth.objects.filter(student=student, status=False)

        for attendance_per_month in attendance_per_months:
            total_debt += attendance_per_month.total_debt
            remaining_debt += attendance_per_month.remaining_debt

        if remaining_debt == 0:
            student.debt_status = 0
        elif student.total_payment_month > total_debt:
            student.debt_status = 1
            TeacherBlackSalary.objects.filter(student=student, status=False).update(status=True)
        elif student.total_payment_month < total_debt:
            student.debt_status = 2

        student.save()
        return Response(attendance_per_months)


class shahakota(APIView):
    def post(self, request):
        from attendances.models import AttendancePerMonth
        attendance_id=request.data['id']
        print(attendance_id)
        month = AttendancePerMonth.objects.get(id=attendance_id, status=False)
        if month.remaining_debt == 0:
            data = {
                'price': month.total_debt
            }
        else:
            data = {
                'price': month.remaining_debt
            }
        return Response(data)
