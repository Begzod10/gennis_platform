from datetime import date

from django.db import models


class Term(models.Model):
    QUARTER_CHOICES = ((1, "1-chorak"), (2, "2-chorak"), (3, "3-chorak"), (4, "4-chorak"),)

    quarter = models.PositiveSmallIntegerField(choices=QUARTER_CHOICES, editable=False)
    start_date = models.DateField()
    end_date = models.DateField()
    academic_year = models.CharField(max_length=9, editable=False)  # Masalan: "2024-2025"

    def save(self, *args, **kwargs):
        """
        O‘zbekiston maktab o‘quv yiliga mos ravishda chorak va o‘quv yilini aniqlash.
        """
        year = self.start_date.year

        if self.start_date.month < 9:
            year -= 1

        if date(year, 9, 2) <= self.start_date <= date(year, 10, 26):
            self.quarter = 1
        elif date(year, 11, 4) <= self.start_date <= date(year, 12, 28):
            self.quarter = 2
        elif date(year + 1, 1, 13) <= self.start_date <= date(year + 1, 3, 22):
            self.quarter = 3
        elif date(year + 1, 3, 31) <= self.start_date <= date(year + 1, 6, 2):
            self.quarter = 4
        else:
            raise ValueError(f"Berilgan sana ({self.start_date}) hech bir chorakka to‘g‘ri kelmadi!")

        self.academic_year = f"{year}-{year + 1}"

        super().save(*args, **kwargs)


class Test(models.Model):
    name = models.CharField(max_length=255)
    weight = models.IntegerField()
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE)
    group = models.ForeignKey('group.Group', on_delete=models.CASCADE)
    class_number = models.ForeignKey('classes.ClassNumber', on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)


class Assignment(models.Model):
    percentage = models.IntegerField()
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
