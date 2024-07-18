from rest_framework import serializers

from .models import Book, BookImage, CollectedBookPayments, BalanceOverhead, BookOrder, CenterBalance, CenterOrders


class BookOrderSerializers(serializers.ModelSerializer):
    class Meta:
        model = BookOrder
        fields = '__all__'

    def update(self, instance, validated_data):
        admin_status = validated_data.pop('admin_status', None)
        if admin_status and admin_status == True:
            branch = validated_data.pop('branch', None)
            payment_type = validated_data.pop('payment_type', None)
            CollectedBookPayments.objects.get_or_create(branch=branch, payment_type=payment_type,
                                                        total_debt=validated_data.pop('total_debt'),
                                                        month_date=validated_data.pop('month_date'))
            instance.admin_status = True
            instance.save()
        else:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
        instance.save()
        return instance


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


class CenterBalanceSerializers(serializers.ModelSerializer):
    class Meta:
        model = CenterBalance
        fields = '__all__'


class CenterOrdersSerializers(serializers.ModelSerializer):
    class Meta:
        model = CenterOrders
        fields = '__all__'
