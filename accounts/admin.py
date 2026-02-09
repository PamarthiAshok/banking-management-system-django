from django.contrib import admin
from .models import BankAccount, Transaction


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = (
        'display_account_number',
        'full_name',
        'phone_number',
        'account_balance',
        'is_active',
        'created_at'
    )
    search_fields = ('full_name', 'phone_number', 'email')
    list_filter = ('is_active', 'gender')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'account',
        'transaction_type',
        'amount',
        'balance_after_transaction',
        'created_at'
    )
    list_filter = ('transaction_type',)
    search_fields = ('account__full_name',)
