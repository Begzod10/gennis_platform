from django.db.models.signals import post_delete
from django.dispatch import receiver


@receiver(post_delete, sender='school_time_table.ClassTimeTable')
def clear_observation_schedule_timetable(sender, instance, **kwargs):
    """
    When a ClassTimeTable entry is deleted, clear the time_table FK on any
    TeacherObservationSchedule rows that referenced it.
    """
    from observation.models import TeacherObservationSchedule
    TeacherObservationSchedule.objects.filter(time_table=instance).update(time_table=None)
