import pprint

from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import GroupSubjectSerializer, GroupListSerializer
from group.models import Group, GroupSubjects
from rest_framework import generics
from classes.models import ClassNumber, ClassNumberSubjects
from students.models import StudentSubject
from django.db.models import Q, Case, When, Value, BooleanField, Avg
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta, date

from terms.models import Term
from flows.models import Flow
from school_time_table.models import ClassTimeTable
from attendances.models import StudentScoreByTeacher


class GroupStudentsClassRoom(APIView):
    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        list = []
        group = Group.objects.get(pk=pk)
        for student in group.students.all():
            list.append({
                'id': student.id,
                'name': student.user.name,
                "surname": student.user.surname,
                "father_name": student.user.father_name,
                "phone_number": student.user.phone,
                "birth_date": student.user.birth_date.isoformat(),
                "balance": student.id,
                "username": student.user.username

            })
        return Response(list)


class GroupListView(generics.ListAPIView):
    serializer_class = GroupListSerializer

    def get_queryset(self):
        branch_id = self.request.query_params.get("branch_id")
        if not branch_id:
            raise ValidationError({"branch_id": "This query param is required."})

        class_type_id = self.request.query_params.get("class_type_id")

        base = (
            Group.objects.filter(branch_id=branch_id, deleted=False)
            .select_related("class_number", "color", "class_type")
            .prefetch_related("group_subjects__subject")
        )

        if class_type_id:
            qs = base.filter(
                Q(class_type_id=class_type_id) | Q(class_type_id__isnull=True)
            ).annotate(
                status_class_type=Case(
                    When(class_type_id=class_type_id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
        else:
            qs = base.filter(class_type_id__isnull=True).annotate(
                status_class_type=Value(False, output_field=BooleanField())
            )

        return qs.order_by("class_number_id")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data})


class GroupSubjectAddView(APIView):
    def post(self, request, *args, **kwargs):
        subjects = request.data.get('subjects', [])
        group_id = request.query_params.get('group_id')
        group = Group.objects.get(pk=group_id)

        for subject in subjects:
            subject_id = subject['value']
            hours = subject.get('hours', 0)

            group_subject, created = GroupSubjects.objects.get_or_create(
                group=group,
                subject_id=subject_id,
                defaults={'hours': hours}
            )
            if not created:
                group_subject.hours = hours
                group_subject.save()

            for st in group.students.all():
                student_subject, st_created = StudentSubject.objects.get_or_create(
                    student=st,
                    group_subjects=group_subject,
                    subject_id=subject_id,
                    defaults={'hours': hours}
                )
                if not st_created:
                    student_subject.hours = hours
                    student_subject.save()

        data = GroupListSerializer(group).data
        return Response(data)


class GroupSubjectRemoveView(APIView):
    def post(self, request, *args, **kwargs):
        subject = request.data['subject_id']
        group = Group.objects.get(pk=request.data['group_id'])
        group_subject = GroupSubjects.objects.filter(group_id=group.id, subject_id=subject)
        group_subject.delete()
        data = GroupListSerializer(group).data
        return Response({
            "msg": "O'zgartirildi",
        })


class AddClassTypeToGroup(APIView):
    def post(self, request, *args, **kwargs):
        group = Group.objects.get(pk=request.data['group_id'])
        if group.class_type_id:
            group.class_type_id = None
        else:
            group.class_type_id = request.data['class_type_id']
        group.save()
        return Response({
            "msg": "success"
        })


class GroupFlowRatingReportView(APIView):
    def get(self, request):
        group_id = request.query_params.get('group_id')
        flow_id = request.query_params.get('flow_id')
        is_flow = request.query_params.get('is_flow') in ['true', 'True', '1']

        target_id = flow_id if is_flow else group_id
        if not target_id:
            return Response({"detail": "group_id yoki flow_id talab qilinadi"}, status=400)

        today = timezone.now().date()
        term = Term.objects.filter(start_date__lte=today, end_date__gte=today).first()
        
        if term:
            start_date = term.start_date
            end_date = term.end_date
        else:
            start_date = today.replace(day=1)
            end_date = today

        if is_flow:
            try:
                entity = Flow.objects.get(pk=target_id)
                branch_id = entity.branch_id
                filter_kwargs = {'flow': entity}
                timetable_filter = {'flow': entity}
            except Flow.DoesNotExist:
                return Response({"detail": "Flow topilmadi"}, status=404)
        else:
            try:
                entity = Group.objects.get(pk=target_id)
                branch_id = entity.branch_id
                filter_kwargs = {'group': entity}
                timetable_filter = {'group': entity}
            except Group.DoesNotExist:
                return Response({"detail": "Group topilmadi"}, status=404)

        # 3. Timetable info
        timetable = ClassTimeTable.objects.filter(**timetable_filter).select_related(
            'week', 'hours', 'teacher', 'subject', 'teacher__user'
        ).order_by('week__order', 'hours__start_time')


        # 4. Students list
        students = entity.students.all().select_related('user')
        student_ids = [s.id for s in students]

        # 5. Scores per subject (using teacher as proxy since score model lacks subject)
        teacher_subjects = {}
        for item in timetable:
            if item.teacher_id and item.subject:
                teacher_subjects[item.teacher_id] = item.subject.name

        subject_scores = []
        for t_id, s_name in teacher_subjects.items():
            # Fetch all individual records for the period and subject (teacher)
            records = StudentScoreByTeacher.objects.filter(
                teacher_id=t_id,
                day__range=[start_date, end_date],
                student_id__in=student_ids,
                **filter_kwargs
            ).order_by('day')

            # Group records by student
            student_history = {s_id: [] for s_id in student_ids}
            for record in records:
                student_history[record.student_id].append({
                    "day": record.day,
                    "status": record.status,
                    "homework": record.homework,
                    "activeness": record.activeness,
                    "average": record.average
                })

            subject_report = {
                "subject": s_name,
                "students": []
            }

            for s in students:
                history = student_history.get(s.id, [])
                total_lessons = len(history)
                attended_lessons = sum(1 for h in history if h['status'])
                
                # Calculate subject average for this student
                if total_lessons > 0:
                    sum_scores = sum(h['average'] for h in history if h['status'])
                    avg_score = round(sum_scores / attended_lessons, 1) if attended_lessons > 0 else 0
                    attendance_percent = round((attended_lessons / total_lessons) * 100, 1)
                else:
                    avg_score = 0
                    attendance_percent = 0

                subject_report["students"].append({
                    "id": s.id,
                    "name": f"{s.user.name} {s.user.surname}",
                    "average_score": avg_score,
                    "attendance_percentage": attendance_percent,
                    "total_lessons": total_lessons,
                    "attended_lessons": attended_lessons,
                    "history": history
                })
            
            subject_scores.append(subject_report)

        # 6. Overall average for students in this entity
        overall_scores = StudentScoreByTeacher.objects.filter(
            day__range=[start_date, end_date],
            student_id__in=student_ids,
            **filter_kwargs
        ).values('student_id').annotate(avg_total=Avg('average'))

        overall_map = {item['student_id']: item['avg_total'] for item in overall_scores}

        # 7. Branch-wide ranking
        branch_ranking = StudentScoreByTeacher.objects.filter(
            day__range=[start_date, end_date],
            student__user__branch_id=branch_id
        ).values('student_id').annotate(avg_total=Avg('average')).order_by('-avg_total')

        branch_ranking_list = list(branch_ranking)
        branch_rank_map = {item['student_id']: i + 1 for i, item in enumerate(branch_ranking_list)}

        # 8. Class-wide ranking
        sorted_overall = sorted(overall_map.items(), key=lambda x: x[1], reverse=True)
        class_rank_map = {item[0]: i + 1 for i, item in enumerate(sorted_overall)}

        # 9. Assembly
        final_rating = [
            {
                "id": s.id,
                "name": f"{s.user.name} {s.user.surname}",
                "total_average": round(overall_map.get(s.id, 0), 1),
                "rank_class": class_rank_map.get(s.id, len(students)),
                "rank_branch": branch_rank_map.get(s.id, None) 
            }
            for s in students
        ]
        final_rating.sort(key=lambda x: x['total_average'], reverse=True)

        return Response({
            "term": {
                "start": start_date,
                "end": end_date,
                "name": term.quarter if term else "Maxsus davr"
            },
            "subject_scores": subject_scores,
            "overall_rating": final_rating
        })
