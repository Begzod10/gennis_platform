from rest_framework import generics
from rest_framework.response import Response
from ...models import ClassTimeTable
from group.models import Group, GroupSubjects, GroupSubjectsCount
from students.models import Student, StudentSubject, StudentSubjectCount
from ...serializers import ClassTimeTableCreateUpdateSerializers

from datetime import timedelta
from django.db import transaction

import requests
from gennis_platform.settings import classroom_server



class DeleteItemClassTimeTable(generics.RetrieveDestroyAPIView):
    queryset = ClassTimeTable.objects.all()
    serializer_class = ClassTimeTableCreateUpdateSerializers

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()


        # Anchor week by the instance date
        ref_date = instance.date if hasattr(instance, "date") else None
        if ref_date is None:
            return Response({"detail": "ClassTimeTable.date is required."}, status=400)

        monday = ref_date - timedelta(days=ref_date.weekday())  # start of week (Mon)
        friday = monday + timedelta(days=4)  # end of week (Fri)

        # Serializerga instance berish kerak
        serializer = self.get_serializer(instance)

        # Avval flask serverdan o‘chirib tashlaymiz
        flask_response, status_code = serializer.delete_from_flask(instance)


        with transaction.atomic():
            # --- GROUP-LEVEL COUNTS (only if lesson is for a group) ---
            if instance.group:
                group_subjects = GroupSubjects.objects.filter(
                    group=instance.group, subject=instance.subject
                ).first()

                if group_subjects:
                    # Delete the per-lesson aggregate row tied to this timetable (if exists)
                    gs_count_row = GroupSubjectsCount.objects.filter(
                        class_time_table=instance, group_subjects=group_subjects
                    ).first()
                    if gs_count_row:
                        gs_count_row.delete()

                    # Recompute remaining count for the SAME WEEK (Mon→Fri), excluding this lesson
                    other_group_subjects = GroupSubjectsCount.objects.filter(
                        group_subjects=group_subjects,
                        date__gte=monday,
                        date__lte=friday,
                    ).exclude(class_time_table=instance).count()

                    # Persist the recalculated weekly count on GroupSubjects (if you store it there)
                    # If `group_subjects.count` represents something else (e.g., monthly),
                    # replace this with the correct target field or remove it.
                    group_subjects.count = other_group_subjects
                    group_subjects.save(update_fields=["count"])

            # --- STUDENT-LEVEL COUNTS ---
            # Determine the subject (group subject or flow subject)
            subject = instance.subject if instance.subject else (instance.flow.subject if instance.flow else None)
            if subject:
                # For each student in this class, remove the per-lesson count row
                for student in instance.students.all():
                    student_subject = StudentSubject.objects.filter(
                        student=student, subject=subject
                    ).first()

                    if student_subject:
                        ss_count_row = StudentSubjectCount.objects.filter(
                            class_time_table=instance,
                            student_subjects=student_subject
                        ).first()
                        if ss_count_row:
                            ss_count_row.delete()
            self.perform_destroy(instance)

        return Response({
            "msg": "Dars muvvaffaqqiyatli o'chirildi"
        }, status=200)
