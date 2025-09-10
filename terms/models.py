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
        O‘zbekiston ta'lim yili qoidalariga ko‘ra chorak va o‘quv yilini aniqlaydi.
        """
        month = self.start_date.month
        day = self.start_date.day

        if date(self.start_date.year, 9, 2) <= self.start_date <= date(self.start_date.year, 10, 26):
            self.quarter = 1
        elif date(self.start_date.year, 11, 4) <= self.start_date <= date(self.start_date.year, 12, 28):
            self.quarter = 2
        elif date(self.start_date.year + 1, 1, 13) <= self.start_date <= date(self.start_date.year + 1, 3, 22):
            self.quarter = 3
        elif date(self.start_date.year + 1, 3, 31) <= self.start_date <= date(self.start_date.year + 1, 6, 2):
            self.quarter = 4
        else:
            raise ValueError("Sana o‘quv yilidagi hech bir chorakka to‘g‘ri kelmadi.")

        if self.quarter in [1, 2]:
            self.academic_year = f"{self.start_date.year}-{self.start_date.year + 1}"
        else:
            self.academic_year = f"{self.start_date.year - 1}-{self.start_date.year}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_quarter_display()} ({self.academic_year})"


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
