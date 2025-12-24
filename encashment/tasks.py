from celery import shared_task
from django.db.models import Prefetch, Q, Sum
from django.utils import timezone

from branch.models import Branch
from encashment.models import DailySummary
from group.models import Group
from students.models import Student, DeletedNewStudent, DeletedStudent, StudentPayment


def active_students(branch_id):
    deleted_student_ids = DeletedStudent.objects.filter(student__groups_student__isnull=True,
                                                        deleted=False).values_list('student_id', flat=True)

    deleted_new_student_ids = DeletedNewStudent.objects.values_list('student_id', flat=True)

    active_students = Student.objects.select_related('user', 'user__language', 'class_number').prefetch_related(
        'user__student_user',
        Prefetch('groups_student', queryset=Group.objects.select_related('class_number', 'color').order_by('id'),
                 to_attr='prefetched_groups')).exclude(id__in=deleted_student_ids).exclude(
        id__in=deleted_new_student_ids).filter(groups_student__isnull=False,
                                               user__branch_id=branch_id).distinct().order_by(
        'class_number__number')
    return active_students.count()


def new_students(branch_id):
    excluded_ids = list(DeletedStudent.objects.filter(deleted=False).values_list('student_id', flat=True)) + list(
        DeletedNewStudent.objects.values_list('student_id', flat=True))

    return Student.objects.filter(
        ~Q(id__in=excluded_ids, user__branch_id=branch_id) & Q(groups_student__isnull=True)).distinct().order_by(
        '-pk').count()


def new_deleted_students(branch_id):
    return DeletedNewStudent.objects.filter(student__user__branch_id=branch_id).count()


def deleted_students(branch_id):
    deleted_new_student_ids = DeletedNewStudent.objects.values_list('student_id', flat=True)
    deleted = DeletedStudent.objects.filter(deleted=False).values_list('student_id', flat=True)

    queryset = DeletedStudent.objects.filter(student__id__in=deleted, deleted=False,
                                             student__user__branch_id=branch_id).exclude(
        student__id__in=deleted_new_student_ids).order_by('-deleted_date')
    return queryset.count()


def total_payments_and_sum(branch_id):
    payments = StudentPayment.objects.filter(branch_id=branch_id).values()
    result = payments.aggregate(total=Sum('payment_sum'))
    return payments.count(), result['total'] or 0


@shared_task
def daily_summary():
    today = timezone.now().date()
    branches = Branch.objects.all()

    for branch in branches:
        total_students = active_students(branch.id)
        new_students_count = new_students(branch.id)
        deleted_students_count = deleted_students(branch.id)
        new_deleted_students_count = new_deleted_students(branch.id)
        total_payments, total_payments_sum = total_payments_and_sum(branch.id)

        present_students = total_students

        DailySummary.objects.update_or_create(
            date=today,
            branch=branch,
            defaults={
                "total_students": total_students,
                "new_students": new_students_count,
                "deleted_students": deleted_students_count,
                "present_students": present_students,
                "new_deleted_students": new_deleted_students_count,
                "total_payments": total_payments,
                "total_payments_sum": total_payments_sum or 0,
            }
        )
