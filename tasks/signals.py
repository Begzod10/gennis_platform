from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Mission, Notification


def send_notification(user, mission, message, role):
    Notification.objects.create(
        user=user,
        mission=mission,
        message=message,
        role=role,
        deadline=mission.deadline,
    )


# -------------------------
# NEW — Mission NEW CREATED
# -------------------------
@receiver(post_save, sender=Mission)
def mission_created(sender, instance, created, **kwargs):
    if created:
        executor = instance.executor
        send_notification(
            executor,
            instance,
            f"Sizga yangi vazifa berildi: {instance.title}. Deadline: {instance.deadline}",
            "executor"
        )


# ------------------------------------
# STATUS change (old code improved)
# ------------------------------------
@receiver(pre_save, sender=Mission)
def mission_status_changed(sender, instance, **kwargs):
    if not instance.pk:
        return

    old = Mission.objects.get(pk=instance.pk)
    old_status = old.status
    new_status = instance.status

    if old_status == new_status:
        return

    executor = instance.executor
    creator = instance.creator
    reviewer = instance.reviewer

    # Executor started work
    if new_status == "in_progress":
        send_notification(
            creator,
            instance,
            f"{executor.first_name} vazifani boshladi: {instance.title}",
            "creator"
        )

    # Executor finished work → reviewer must check
    if new_status == "completed" and reviewer:
        send_notification(
            reviewer,
            instance,
            f"{executor.first_name} '{instance.title}' vazifasini tugatdi. Ko‘rib chiqing.",
            "reviewer"
        )

    if new_status == "approved":
        send_notification(
            executor,
            instance,
            f"'{instance.title}' tasdiqlandi.",
            "executor"
        )

    if new_status == "recheck":
        send_notification(
            executor,
            instance,
            f"'{instance.title}' qayta tekshirish uchun qaytarildi.",
            "executor"
        )

    if new_status == "declined":
        send_notification(
            executor,
            instance,
            f"'{instance.title}' rad qilindi.",
            "executor"
        )
