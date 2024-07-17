from rest_framework import serializers

from .models import Book, BookImage, CollectedBookPayments, BalanceOverhead, BookOrder, CenterBalance, CenterOrders


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'name', 'desc', 'price', 'own_price', 'share_price', 'file']


class BookImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookImage
        fields = ['id', 'image', 'book']


class CollectedBookPaymentsSerializers(serializers.ModelSerializer):
    class Meta:
        model = CollectedBookPayments
        fields = '__all__'


class BalanceOverheadSerializers(serializers.ModelSerializer):
    class Meta:
        model = BalanceOverhead
        fields = '__all__'


class BookOrderSerializers(serializers.ModelSerializer):
    class Meta:
        model = BookOrder
        fields = '__all__'


class CenterBalanceSerializers(serializers.ModelSerializer):
    class Meta:
        model = CenterBalance
        fields = '__all__'


class CenterOrdersSerializers(serializers.ModelSerializer):
    class Meta:
        model = CenterOrders
        fields = '__all__'
