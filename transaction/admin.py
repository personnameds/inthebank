from django.contrib import admin
from .models import Transaction, ScheduledTransaction, SavedTransaction

class TransactionAdmin(admin.ModelAdmin):
	list_filter=('category',)

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(ScheduledTransaction)
admin.site.register(SavedTransaction)