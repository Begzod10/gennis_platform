from django.db.models import Count, Min, Max, Q
from students.models import StudentSubject
from group.models import GroupSubjects
from collections import defaultdict


def all_weekly_counts_equal(gs: GroupSubjects, monday, friday) -> bool:
    qs = (StudentSubject.objects
    .filter(group_subjects=gs)
    .annotate(week_total=Count(
        'student_subject_count',
        filter=Q(student_subject_count__date__gte=monday,
                 student_subject_count__date__lte=friday)
    )))
    agg = qs.aggregate(min_w=Min('week_total'), max_w=Max('week_total'))
    status = agg['min_w'] == agg['max_w']
    return status, agg


def weekly_mismatch_details(gs: GroupSubjects, monday, friday):
    buckets = defaultdict(list)
    qs = (StudentSubject.objects
    .filter(group_subjects=gs)
    .annotate(week_total=Count(
        'student_subject_count',
        filter=Q(student_subject_count__date__gte=monday,
                 student_subject_count__date__lte=friday)
    )))
    for ss in qs:
        buckets[ss.week_total].append(ss.student_id)
    return buckets
