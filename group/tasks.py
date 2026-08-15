import logging
import os
from celery import shared_task
from datetime import datetime
from django.db import transaction
from django.db.models import Q

from classes.models import ClassNumber
from group.models import Group
from students.models import Student, StudentHistoryGroups

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


def _move_student_groups(student, old_class_number, new_class_number, today):
    """
    Talabaning `old_class_number`ga tegishli, hozir a'zo bo'lgan guruhlarini
    branch + til + rang mos keladigan `new_class_number`dagi guruhga ko'chiradi.

    Har bir eski guruh uchun mos yangi guruh topilsa: M2M yangilanadi va
    StudentHistoryGroups'da eski a'zolik yopiladi (left_day), yangisi ochiladi (joined_day).
    Mos guruh topilmasa: talaba eski guruhida qoldiriladi, xatolik sifatida loglanadi.

    Qaytaradi: (moved_count, skipped_count)
    """
    moved_count = 0
    skipped_count = 0

    old_groups = student.groups_student.filter(class_number=old_class_number, deleted=False)

    for old_group in old_groups:
        target_group = Group.objects.filter(
            branch=old_group.branch,
            class_number=new_class_number,
            language=old_group.language,
            color=old_group.color,
            deleted=False,
        ).order_by('id').first()

        if target_group is None:
            skipped_count += 1
            logger.error(
                "Mos guruh topilmadi: Talaba ID %d, eski guruh ID %d (branch: %s, til: %s, rang: %s, sinf: %d). "
                "Talaba eski guruhida qoldirildi.",
                student.id, old_group.id, old_group.branch_id, old_group.language_id, old_group.color_id,
                new_class_number.number,
            )
            continue

        old_group.students.remove(student)
        target_group.students.add(student)

        StudentHistoryGroups.objects.filter(
            student=student, group=old_group, left_day__isnull=True
        ).order_by('-joined_day').update(left_day=today)

        StudentHistoryGroups.objects.create(
            student=student, group=target_group, reason="class_promotion", joined_day=today,
        )

        moved_count += 1
        logger.info(
            "Talaba (ID: %d) guruh ID %d dan guruh ID %d ga o'tkazildi (sinf %d -> %d).",
            student.id, old_group.id, target_group.id, old_class_number.number, new_class_number.number,
        )

    return moved_count, skipped_count


@shared_task
def update_class_task():
    today = datetime.today()
    logger.info("update_class_task boshlandi. Sana: %s", today.strftime("%Y-%m-%d"))

    if today.month != 8:
        logger.warning("Avgust emas (%d-oy). Vazifa o'tkazib yuborildi.", today.month)
        return "Task skipped — only runs in August"

    today_date = today.date()

    students = Student.objects.select_related('user', 'class_number').filter(
        Q(user__registered_date__month__gte=9) | Q(user__registered_date__month__lte=6),
        class_number__isnull=False
    )

    logger.info("Qidiruv bo'yicha %d ta talaba topildi.", students.count())

    updated_count = 0
    errors_count = 0
    groups_moved_count = 0
    groups_skipped_count = 0

    with transaction.atomic():
        for student in students:
            logger.debug("Talaba: %s (ID: %d, Hozirgi sinf: %d)",
                         student.user.username, student.id, student.class_number.number)

            if student.class_number.number >= 11:
                logger.debug("Talaba (ID: %d) 11-sinfda yoki undan yuqorida.", student.id)
                continue

            if student.class_number.number <= 0:
                logger.debug("Talaba (ID: %d) 0-sinfda (tayyorlov). Avtomatik o'tkazishga tegishli emas.", student.id)
                continue

            current_class_number = student.class_number

            try:
                next_class_number = ClassNumber.objects.get(
                    number=current_class_number.number + 1,
                    branch=current_class_number.branch
                )

                moved, skipped = _move_student_groups(student, current_class_number, next_class_number, today_date)
                groups_moved_count += moved
                groups_skipped_count += skipped

                student.class_number = next_class_number
                student.save(update_fields=["class_number"])
                updated_count += 1

                logger.info("Talaba (ID: %d) %d-sinfdan %d-sinfga o'tkazildi.",
                            student.id, current_class_number.number, next_class_number.number)

            except ClassNumber.DoesNotExist:
                errors_count += 1
                logger.error("Keyingi sinf topilmadi: Talaba ID %d, hozirgi sinf %d, branch: %s, class_types: %s",
                             student.id, current_class_number.number, current_class_number.branch,
                             current_class_number.class_types)
            except Exception as e:
                errors_count += 1
                logger.exception("Talabani o'tkazishda xatolik: Talaba ID %d", student.id)

    logger.info(
        "Yakunlandi. Jami %d talaba o'tkazildi, %d ta xatolik, %d ta guruh a'zoligi ko'chirildi, "
        "%d ta guruh a'zoligi mos guruh topilmagani sababli ko'chirilmadi.",
        updated_count, errors_count, groups_moved_count, groups_skipped_count,
    )

    result_message = f"{updated_count} students promoted, {groups_moved_count} group memberships moved"
    if groups_skipped_count > 0:
        result_message += f", {groups_skipped_count} group memberships could not be moved (no matching group)"
    if errors_count > 0:
        result_message += f", {errors_count} errors occurred"

    return result_message
