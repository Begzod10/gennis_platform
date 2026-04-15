from django.db.models.signals import post_delete
from django.dispatch import receiver

from observation.models import TeacherObservationDay


@receiver(post_delete, sender=TeacherObservationDay)
def revert_observation_schedule(sender, instance, **kwargs):
    """
    When a TeacherObservationDay is deleted, revert any linked
    TeacherObservationSchedule entries back to incomplete.
    """
    from observation.models import TeacherObservationSchedule
    TeacherObservationSchedule.objects.filter(observation_day=instance).update(
        is_completed=False,
        observation_day=None,
    )
