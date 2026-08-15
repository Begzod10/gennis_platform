"""
Umumiy sinxronlash: `update_class_task` ilgari (guruh ko'chirish logikasi
qo'shilishidan oldin, masalan 2025-08-10 va 2026-08-10dagi ishga tushishlarida)
talabaning `class_number`sini oshirgan, lekin uni yangi sinfga mos guruhga
o'tkazmagan holatlarni tuzatadi.

Har bir talaba uchun: hozirgi guruhi(lari)ning `class_number`si talabaning
o'z `class_number`siga TENG EMAS bo'lsa — branch+til+rang mos keladigan,
talabaning haqiqiy `class_number`siga tegishli guruh qidiriladi va talaba
o'sha guruhga ko'chiriladi (StudentHistoryGroups'da tarix bilan).

Mos guruh topilmasa — talaba eski guruhida qoldiriladi, xatolik loglanadi.

Ishlatish:
    python manage.py sync_students_to_class_groups --dry-run
    python manage.py sync_students_to_class_groups
    python manage.py sync_students_to_class_groups --branch-id 5
"""
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from group.tasks import _move_student_groups, logger as task_logger
from students.models import DeletedNewStudent, DeletedStudent, Student


class Command(BaseCommand):
    help = (
        "Class_number'i o'zgargan-u, guruhi eski sinfda qolib ketgan talabalarni "
        "class_number'iga mos (branch+til+rang) guruhga ko'chiradi."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Hech narsani saqlamasdan, nima qilinishini faqat chiqarib ko'rsatadi.",
        )
        parser.add_argument(
            "--branch-id",
            type=int,
            default=None,
            help="Faqat shu branch'dagi talabalarni tekshiradi. Bo'lmasa — barcha branch'lar.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        branch_id = options["branch_id"]
        today_date = date.today()

        excluded_ids = list(
            DeletedStudent.objects.filter(deleted=False).values_list("student_id", flat=True)
        ) + list(DeletedNewStudent.objects.values_list("student_id", flat=True))

        students = (
            Student.objects.select_related("user", "class_number")
            .prefetch_related("groups_student")
            .filter(class_number__isnull=False)
            .exclude(id__in=excluded_ids)
            .order_by("id")
        )
        if branch_id is not None:
            students = students.filter(class_number__branch_id=branch_id)

        checked_count = 0
        students_moved_count = 0
        groups_moved_count = 0
        groups_skipped_count = 0

        with transaction.atomic():
            for student in students:
                checked_count += 1
                mismatched_groups = [
                    g for g in student.groups_student.all()
                    if not g.deleted and g.class_number_id != student.class_number_id
                ]
                if not mismatched_groups:
                    continue

                old_class_numbers = {g.class_number_id: g.class_number for g in mismatched_groups if g.class_number_id}

                self.stdout.write(
                    f"Talaba ID {student.id} ({student.user.username}): joriy sinf "
                    f"{student.class_number.number}, mos kelmagan guruhlar: "
                    f"{[g.id for g in mismatched_groups]}"
                )

                student_moved_any = False
                for old_cn in old_class_numbers.values():
                    try:
                        moved, skipped = _move_student_groups(student, old_cn, student.class_number, today_date)
                    except Exception:
                        task_logger.exception(
                            "[sync] Talaba ID %d guruhini ko'chirishda xatolik (sinf %s -> %s).",
                            student.id, old_cn.number, student.class_number.number,
                        )
                        continue
                    groups_moved_count += moved
                    groups_skipped_count += skipped
                    if moved:
                        student_moved_any = True

                if student_moved_any:
                    students_moved_count += 1

            if dry_run:
                transaction.set_rollback(True)

        summary = (
            f"{'[DRY-RUN] ' if dry_run else ''}Tekshirildi: {checked_count} talaba. "
            f"{students_moved_count} talabaning guruhi to'g'irlandi "
            f"({groups_moved_count} ta guruh a'zoligi ko'chirildi, "
            f"{groups_skipped_count} ta mos guruh topilmagani sababli ko'chirilmadi)."
        )
        self.stdout.write(self.style.SUCCESS(summary))
