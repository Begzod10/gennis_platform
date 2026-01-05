from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from datetime import timedelta
from tasks.models import Mission


class RecurringTaskMiddleware(MiddlewareMixin):

    def process_request(self, request):
        """
        Har bir API requestda recurring tasklarni tekshiradi.
        Cron, Celery, Task Scheduler KERAK EMAS.
        """
        today = timezone.now().date()

        # Faqat recurring tasklarni olamiz
        recurring_tasks = Mission.objects.filter(is_recurring=True)

        for task in recurring_tasks:

            interval = task.repeat_every or 1  # default = 1 kun

            # Bugun task allaqachon yaratilgan bo‘lsa — o‘tkazib yuboramiz
            if task.last_generated == today:
                continue

            # Qachon yangi task yaratilishi kerakligini hisoblaymiz
            next_generate_day = task.deadline + timedelta(days=interval)

            # Agar bugungi sana keyingi yaratilish sanasidan katta bo‘lsa → yangi task yaratamiz
            if today >= next_generate_day:
                self.create_new_task(task, next_generate_day, today)

        return None

    def create_new_task(self, old_task, new_deadline, today):
        """
        Eski taskdan nusxa olib yangi task yaratadi.
        deadline = old.deadline + interval
        """
        new_task = Mission.objects.create(
            title=old_task.title,
            description=old_task.description,
            creator=old_task.creator,
            executor=old_task.executor,
            reviewer=old_task.reviewer,
            branch=old_task.branch,
            status="not_started",
            deadline=new_deadline,
            is_recurring=True,
            repeat_every=old_task.repeat_every
        )

        # Bir kunda takrorlanmasligi uchun
        old_task.last_generated = today
        old_task.save()


