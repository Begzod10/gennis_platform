import logging
import os
from celery import shared_task
from datetime import datetime
from django.db import transaction
from django.db.models import Q

from classes.models import ClassNumber
from students.models import Student

# Set up logging directory
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, 'update_class_task.log')

# Create a logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Avoid adding handlers multiple times
if not logger.handlers:
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


@shared_task
def update_class_task():
    today = datetime.today()
    logger.info("update_class_task boshlandi. Sana: %s", today.strftime("%Y-%m-%d"))

    if today.month != 8:
        logger.warning("Avgust emas (%d-oy). Vazifa o'tkazib yuborildi.", today.month)
        return "Task skipped — only runs in August"

    students = Student.objects.select_related('user', 'class_number').filter(
        Q(user__registered_date__month__gte=9) | Q(user__registered_date__month__lte=6),
        class_number__isnull=False
    ).exclude(user__branch__name="Chirchiq")

    logger.info("Qidiruv bo'yicha %d ta talaba topildi.", students.count())

    updated_count = 0
    errors_count = 0

    with transaction.atomic():
        for student in students:
            logger.debug("Talaba: %s (ID: %d, Hozirgi sinf: %d)",
                         student.user.username, student.id, student.class_number.number)

            if student.class_number.number >= 11:
                logger.debug("Talaba (ID: %d) 11-sinfda yoki undan yuqorida.", student.id)
                continue

            current_class_number = student.class_number.number

            try:
                next_class_number = ClassNumber.objects.get(
                    number=current_class_number + 1,
                    branch=student.class_number.branch
                )

                student.class_number = next_class_number
                student.save(update_fields=["class_number"])
                updated_count += 1

                logger.info("Talaba (ID: %d) %d-sinfdan %d-sinfga o'tkazildi.",
                            student.id, current_class_number, next_class_number.number)

            except ClassNumber.DoesNotExist:
                errors_count += 1
                logger.error("Keyingi sinf topilmadi: Talaba ID %d, hozirgi sinf %d, branch: %s, class_types: %s",
                             student.id, current_class_number, student.class_number.branch,
                             student.class_number.class_types)
            except Exception as e:
                errors_count += 1
                logger.exception("Talabani o'tkazishda xatolik: Talaba ID %d", student.id)

    logger.info("Yakunlandi. Jami %d talaba o'tkazildi, %d ta xatolik.",
                updated_count, errors_count)

    result_message = f"{updated_count} students promoted"
    if errors_count > 0:
        result_message += f", {errors_count} errors occurred"

    return result_message
