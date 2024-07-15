from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=250)
    desc = models.CharField()
    price = models.IntegerField()
    own_price = models.IntegerField()
    share_price = models.IntegerField()
    file = models.FileField(upload_to='books/files', null=True)


class BookImage(models.Model):
    image = models.ImageField(upload_to='books/images',null=True)
    book = models.ForeignKey(Book, related_name='book_image_book_id', on_delete=models.CASCADE)
# class BookOrder(models.Model):
#     user =