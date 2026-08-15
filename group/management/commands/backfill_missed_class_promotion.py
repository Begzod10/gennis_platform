"""
Bir martalik backfill: `update_class_task` (group/tasks.py) filteri
`registered_date__month` 7 va 8 (iyul, avgust)ni butunlay tashlab ketardi
(faqat oy tekshirilar, yil tekshirilmasdi — Q(month__gte=9) | Q(month__lte=6)).

Natijada 2024- va 2025-yillarning iyul/avgustida ro'yxatdan o'tgan talabalar
o'sha yillarning avgustida ishlagan `update_class_task` tomonidan sinfdan-sinfga
o'tkazilmagan bo'lib qolishi mumkin edi.

Bu buyruq shu talabalarni topib:
  1) class_number'ini bir marta +1 qiladi,
  2) yangi class_number bo'yicha mos (branch+til+rang) guruhga o'tkazadi.

11-sinf va undan yuqoridagilar, 0-sinf (tayyorlov), shuningdek (yumshoq)
o'chirilgan talabalar chetlab o'tiladi — xuddi asosiy task kabi.

IDEMPOTENTLIK: har bir muvaffaqiyatli o'tkazilgan talaba ID'si
`group/logs/backfill_missed_class_promotion_processed.json` fayliga yoziladi.
Buyruq qayta ishga tushirilsa, shu faylda bor talabalar qayta +1 QILINMAYDI —
shuning uchun buyruqni bir necha marta xavfsiz ishga tushirish mumkin.

Ishlatish:
    python manage.py backfill_missed_class_promotion --dry-run
    python manage.py backfill_missed_class_promotion
    python manage.py backfill_missed_class_promotion --years 2024,2025
"""
import json
import os
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from classes.models import ClassNumber
from group.tasks import _move_student_groups, log_dir, logger as task_logger
from students.models import DeletedNewStudent, DeletedStudent, Student

PROCESSED_FILE = os.path.join(log_dir, "backfill_missed_class_promotion_processed.json")


def _load_processed_ids():
    if not os.path.exists(PROCESSED_FILE):
        return set()
    with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))


def _save_processed_ids(processed_ids):
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(processed_ids), f)


class Command(BaseCommand):
    help = (
        "Backfill: 2024/2025 (yoki --years bilan ko'rsatilgan boshqa yillar) iyul-avgustida "
        "ro'yxatdan o'tgani sababli update_class_task tomonidan o'tkazib yuborilgan talabalarning "
        "class_number'ini bir marta +1 qiladi va mos guruhga o'tkazadi. Idempotent — "
        "avval o'tkazilgan talabalar qayta ishga tushirilganda qayta +1 qilinmaydi."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--years",
            type=str,
            default="2024,2025",
            help="Vergul bilan ajratilgan registered_date yillari (default: 2024,2025).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Hech narsani saqlamasdan, nima qilinishini faqat chiqarib ko'rsatadi.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Avval PROCESSED_FILE'ga yozilgan (allaqachon o'tkazilgan) talabalarni ham qayta ko'rib chiqadi.",
        )

    def handle(self, *args, **options):
        years = [int(y.strip()) for y in options["years"].split(",") if y.strip()]
        dry_run = options["dry_run"]
        force = options["force"]
        today_date = date.today()

        if not years:
            self.stderr.write(self.style.ERROR("--years bo'sh bo'lmasligi kerak."))
            return

        already_processed = set() if force else _load_processed_ids()
        newly_processed = set()

        excluded_ids = list(
            DeletedStudent.objects.filter(deleted=False).values_list("student_id", flat=True)
        ) + list(DeletedNewStudent.objects.values_list("student_id", flat=True))

        year_filter = Q()
        for year in years:
            year_filter |= Q(
                user__registered_date__year=year,
                user__registered_date__month__in=[7, 8],
            )

        students = (
            Student.objects.select_related("user", "class_number")
            .filter(year_filter, class_number__isnull=False)
            .exclude(id__in=excluded_ids)
            .exclude(id__in=already_processed)
            .order_by("id")
        )

        self.stdout.write(
            f"Yillar: {years}. Topilgan talabalar: {students.count()} ta "
            f"(oldin o'tkazilgan {len(already_processed)} ta allaqachon chetlab o'tildi)."
        )

        updated_count = 0
        skipped_count = 0
        errors_count = 0
        groups_moved_count = 0
        groups_skipped_count = 0

        with transaction.atomic():
            for student in students:
                if student.class_number.number >= 11 or student.class_number.number <= 0:
                    skipped_count += 1
                    continue

                current_class_number = student.class_number

                try:
                    next_class_number = ClassNumber.objects.get(
                        number=current_class_number.number + 1,
                        branch=current_class_number.branch,
                    )
                except ClassNumber.DoesNotExist:
                    errors_count += 1
                    self.stderr.write(self.style.WARNING(
                        f"Keyingi sinf topilmadi: Talaba ID {student.id}, "
                        f"hozirgi sinf {current_class_number.number}, branch {current_class_number.branch}"
                    ))
                    continue

                self.stdout.write(
                    f"Talaba ID {student.id} ({student.user.username}, ro'yxatdan o'tgan: "
                    f"{student.user.registered_date}): {current_class_number.number} -> {next_class_number.number}"
                )

                if dry_run:
                    updated_count += 1
                    continue

                moved, skipped = _move_student_groups(student, current_class_number, next_class_number, today_date)
                groups_moved_count += moved
                groups_skipped_count += skipped

                student.class_number = next_class_number
                student.save(update_fields=["class_number"])
                updated_count += 1
                newly_processed.add(student.id)
                task_logger.info(
                    "[backfill] Talaba (ID: %d) %d-sinfdan %d-sinfga o'tkazildi (registered_date: %s).",
                    student.id, current_class_number.number, next_class_number.number,
                    student.user.registered_date,
                )

            if dry_run:
                transaction.set_rollback(True)

        if not dry_run and newly_processed:
            _save_processed_ids(already_processed | newly_processed)

        summary = (
            f"{'[DRY-RUN] ' if dry_run else ''}Yakunlandi. {updated_count} talaba o'tkazildi, "
            f"{skipped_count} ta 11-sinf/0-sinf bo'lgani uchun o'tkazib yuborildi, "
            f"{errors_count} ta xatolik. Guruhlar: {groups_moved_count} ko'chirildi, "
            f"{groups_skipped_count} mos guruh topilmadi."
        )

        self.stdout.write(self.style.SUCCESS(summary))
