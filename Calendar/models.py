from django.db import models


class Years(models.Model):
    year = models.IntegerField()

    def add(self):
        self.save()

    def __str__(self):
        return str(self.year)

    class Meta:
        ordering = ['id']


class Month(models.Model):
    month_number = models.IntegerField()
    month_name = models.CharField(max_length=50)
    years = models.ForeignKey(Years, related_name='months', on_delete=models.CASCADE)

    def add(self):
        self.save()

    def __str__(self):
        return self.month_name

    class Meta:
        ordering = ['id']


class Day(models.Model):
    day_number = models.IntegerField()
    day_name = models.CharField(max_length=50)
    month = models.ForeignKey(Month, related_name='days', on_delete=models.CASCADE)
    year = models.ForeignKey(Years, related_name='days', on_delete=models.CASCADE)
    type_id = models.ForeignKey('TypeDay', on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']


class TypeDay(models.Model):
    type = models.CharField(max_length=255)
    color = models.CharField(max_length=255)

    def add(self):
        self.save()

    class Meta:
        ordering = ['id']
