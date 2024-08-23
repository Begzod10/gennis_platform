import datetime
import os
import uuid
from datetime import datetime

import docx
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from branch.models import Branch
from .models import Student, DeletedStudent, ContractStudent, DeletedNewStudent
from .serializers import StudentCharity
from .serializers import (StudentListSerializer,
                          DeletedStudentListSerializer, DeletedNewStudentListSerializer)
from .utils import user_contract_folder


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


class DeletedFromRegistered(APIView):
    def get(self, request, *args, **kwargs):
        deleted_student_ids = DeletedStudent.objects.values_list('student_id', flat=True)
        delete_new_students = DeletedNewStudent.objects.exclude(id__in=deleted_student_ids)
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            delete_new_students = delete_new_students.filter(branch_id=branch_id)
        if location_id is not None:
            delete_new_students = delete_new_students.filter(location_id=location_id)
        delete_new_student_serializer = DeletedNewStudentListSerializer(delete_new_students, many=True)
        return Response(delete_new_student_serializer.data)


class DeletedGroupStudents(APIView):
    def get(self, request, *args, **kwargs):
        deleted_new_student_ids = DeletedNewStudent.objects.values_list('student_id', flat=True)
        active_students = Student.objects.exclude(id__in=deleted_new_student_ids)
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            active_students = active_students.filter(branch_id=branch_id)
        if location_id is not None:
            active_students = active_students.filter(location_id=location_id)
        student_serializer = StudentListSerializer(active_students, many=True)
        return Response(student_serializer.data)


class NewRegisteredStudents(APIView):
    def get(self, request, *args, **kwargs):
        deleted_student_ids = DeletedStudent.objects.values_list('student_id', flat=True)
        deleted_new_student_ids = DeletedNewStudent.objects.values_list('student_id', flat=True)
        active_students = Student.objects.exclude(id__in=deleted_student_ids) \
            .exclude(id__in=deleted_new_student_ids) \
            .filter(groups_student__isnull=True).distinct()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            active_students = active_students.filter(branch_id=branch_id)
        if location_id is not None:
            active_students = active_students.filter(location_id=location_id)
        active_students = active_students[:100]

        student_serializer = StudentListSerializer(active_students, many=True)

        return Response(student_serializer.data)


class ActiveStudents(APIView):
    def get(self, request, *args, **kwargs):
        deleted_student_ids = DeletedStudent.objects.values_list('student_id', flat=True)
        deleted_new_student_ids = DeletedNewStudent.objects.values_list('student_id', flat=True)
        active_students = Student.objects.exclude(id__in=deleted_student_ids) \
            .exclude(id__in=deleted_new_student_ids) \
            .filter(groups_student__isnull=False).distinct()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            active_students = active_students.filter(branch_id=branch_id)
        if location_id is not None:
            active_students = active_students.filter(location_id=location_id)
        active_students = active_students[:100]

        student_serializer = StudentListSerializer(active_students, many=True)

        return Response(student_serializer.data)


class CreateContractView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        data = request.data

        calendar_year, calendar_month, calendar_day = self._get_calendar_date()
        calendar_year = str(calendar_year)  # Ensure calendar_year is a string
        student = get_object_or_404(Student, user_id=user_id)

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
            (user.name, user.surname, user.father_name) if int(user.age) >= 18
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
            15].text = f"2.1 O‘quvchining nodavlat taʼlim muassasida taʼlim olishi uchun bir oylik to‘lov summasi {abs(student.debt_status) - all_charity} va {contract.expire_date.strftime('%d-%m-%Y')} muddatgacha {abs(((student.debt_status) - all_charity) * month)} so‘mni tashkil etadi."
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
        student = get_object_or_404(ContractStudent, student__user_id=user_id)
        file = request.FILES.get('file')
        if not file:
            return Response({"success": False, "msg": "No file provided"}, status=400)
        upload_folder = user_contract_folder()
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        file_name = str(student.contract)
        file_path = os.path.join(upload_folder, file_name)

        try:
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            url = os.path.join('contracts', file_name)
            student.contract = url
            student.save()

            return Response({"success": True, "msg": "File uploaded successfully", "url": url})

        except Exception as e:
            return Response({"success": False, "msg": f"File upload failed: {str(e)}"}, status=500)
