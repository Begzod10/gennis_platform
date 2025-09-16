from rest_framework import generics
from rest_framework.response import Response
from ...models import ClassTimeTable
from group.models import Group, GroupSubjects, GroupSubjectsCount
from students.models import Student, StudentSubject, StudentSubjectCount
from ...serializers import ClassTimeTableCreateUpdateSerializers


class DeleteItemClassTimeTable(generics.RetrieveDestroyAPIView):
    queryset = ClassTimeTable.objects.all()
    serializer_class = ClassTimeTableCreateUpdateSerializers

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.group:
            group_subjects = GroupSubjects.objects.filter(group=instance.group, subject=instance.subject).first()
            group_subjects_count = GroupSubjectsCount.objects.filter(class_time_table=instance,
                                                                     group_subjects=group_subjects).first()
            other_group_subjects = GroupSubjectsCount.objects.filter(group_subjects=group_subjects,
                                                                     date=instance.date).exclude(
                class_time_table=instance).count()
            if group_subjects_count:
                group_subjects_count.delete()

            group_subjects.count = other_group_subjects
            group_subjects.save()
        subject = instance.subject if instance.subject else instance.flow.subject
        if subject:
            for student in instance.students.all():
                print(student, subject)
                student_subject = StudentSubject.objects.filter(student=student,
                                                                subject=subject).first()
                student_subject_count = StudentSubjectCount.objects.filter(class_time_table=instance,
                                                                           student_subjects=student_subject).first()
                other_student_subjects = StudentSubjectCount.objects.filter(student_subjects=student_subject,
                                                                            date=instance.date).exclude(
                    class_time_table=instance).count()

                if student_subject_count:
                    student_subject_count.delete()
                print("student_subject", student_subject)
                student_subject.count = other_student_subjects
                student_subject.save()

        serializer = self.get_serializer(instance)

        # flask_response, status_code = serializer.delete_from_flask(instance)

        self.perform_destroy(instance)

        return Response({
            "msg": "Dars muvvaffaqqiyatli o'chirildi",
            # "flask_response": flask_response
        }, status=200)
