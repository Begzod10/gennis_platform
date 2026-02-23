from celery import shared_task

from lesson_plan.functions.utils import update_lesson_plan
from school_time_table.models import ClassTimeTable


@shared_task()
def create_lesson_plans():
    class_time_tables = ClassTimeTable.objects.distinct()

    for table in class_time_tables:
        update_lesson_plan.delay(group_id=table.group_id)
    for table in class_time_tables:
        update_lesson_plan.delay(flow_id=table.flow_id)