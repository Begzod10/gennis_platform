from django.db.models.signals import pre_delete
from django.dispatch import receiver

from observation.models import TeacherObservationDay


@receiver(pre_delete, sender=TeacherObservationDay)
def revert_observation_schedule(sender, instance, **kwargs):
    """
    When a TeacherObservationDay is deleted, revert any linked
    TeacherObservationSchedule entries back to incomplete.
    Must use pre_delete because SET_NULL runs before post_delete,
    making the filter match nothing if post_delete is used.
    """
    from observation.models import TeacherObservationSchedule
    TeacherObservationSchedule.objects.filter(observation_day=instance).update(
        is_completed=False,
        observation_day=None,
    )
