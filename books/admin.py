from django.contrib import admin

from .models import (
    Book, BookImage, CollectedBookPayments, BookOrder,
    CenterBalance, EditorBalance, BranchPayment,
    BookOverhead, CenterOrders, BalanceOverhead, UserBook
)


# Register the Book model
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'own_price', 'share_price', 'old_id')
    search_fields = ('name', 'old_id')
    ordering = ('name',)


# Register the BookImage model
@admin.register(BookImage)
class BookImageAdmin(admin.ModelAdmin):
    list_display = ('book', 'image', 'old_id')
    search_fields = ('book__name',)
    ordering = ('id',)


# Register the CollectedBookPayments model
@admin.register(CollectedBookPayments)
class CollectedBookPaymentsAdmin(admin.ModelAdmin):
    list_display = ('branch', 'payment_type', 'total_debt', 'month_date', 'received_date', 'status', 'old_id')
    search_fields = ('branch__name', 'payment_type__name', 'old_id')
    list_filter = ('branch', 'payment_type', 'status', 'month_date', 'received_date')
    ordering = ('-month_date',)


# Register the BookOrder model
@admin.register(BookOrder)
class BookOrderAdmin(admin.ModelAdmin):
    list_display = (
    'user', 'student', 'teacher', 'group', 'book', 'branch', 'count', 'day', 'admin_status', 'editor_status', 'deleted',
    'old_id')
    search_fields = (
    'user__username', 'student__user__username', 'teacher__user__username', 'group__name', 'book__name', 'branch__name',
    'old_id')
    list_filter = ('branch', 'admin_status', 'editor_status', 'deleted', 'day')
    ordering = ('-day',)


# Register the CenterBalance model
@admin.register(CenterBalance)
class CenterBalanceAdmin(admin.ModelAdmin):
    list_display = ('branch', 'total_money', 'remaining_money', 'taken_money', 'month_date', 'old_id')
    search_fields = ('branch__name', 'old_id')
    list_filter = ('branch', 'month_date')
    ordering = ('-month_date',)


# Register the EditorBalance model
@admin.register(EditorBalance)
class EditorBalanceAdmin(admin.ModelAdmin):
    list_display = ('payment_type', 'balance', 'payment_sum', 'overhead_sum', 'date', 'old_id')
    search_fields = ('payment_type__name', 'old_id')
    list_filter = ('payment_type', 'date')
    ordering = ('-date',)


# Register the BranchPayment model
@admin.register(BranchPayment)
class BranchPaymentAdmin(admin.ModelAdmin):
    list_display = ('branch', 'book_order', 'editor_balance', 'payment_type', 'payment_sum', 'old_id')
    search_fields = ('branch__name', 'book_order__book__name', 'editor_balance__payment_type__name', 'old_id')
    list_filter = ('branch', 'payment_type')
    ordering = ('id',)


# Register the BookOverhead model
@admin.register(BookOverhead)
class BookOverheadAdmin(admin.ModelAdmin):
    list_display = ('name', 'deleted_reason', 'payment_type', 'price', 'deleted', 'old_id')
    search_fields = ('name', 'deleted_reason', 'payment_type__name', 'old_id')
    list_filter = ('deleted', 'payment_type')
    ordering = ('id',)


# Register the CenterOrders model
@admin.register(CenterOrders)
class CenterOrdersAdmin(admin.ModelAdmin):
    list_display = ('balance', 'order', 'old_id')
    search_fields = ('balance__branch__name', 'order__book__name', 'old_id')
    list_filter = ('balance__branch',)
    ordering = ('id',)


# Register the BalanceOverhead model
@admin.register(BalanceOverhead)
class BalanceOverheadAdmin(admin.ModelAdmin):
    list_display = ('balance', 'payment_type', 'branch', 'overhead_sum', 'day', 'deleted', 'old_id')
    search_fields = ('balance__branch__name', 'payment_type__name', 'branch__name', 'old_id')
    list_filter = ('balance__branch', 'payment_type', 'deleted', 'day')
    ordering = ('-day',)


# Register the UserBook model
@admin.register(UserBook)
class UserBookAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch', 'book_order', 'teacher_salary', 'user_salary', 'date', 'payment_sum', 'old_id')
    search_fields = (
    'user__username', 'branch__name', 'book_order__book__name', 'teacher_salary__teacher__user__username',
    'user_salary__user__username', 'old_id')
    list_filter = ('branch', 'date')
    ordering = ('-date',)
