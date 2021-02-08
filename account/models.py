from django.db import models

class Account(models.Model):
	name = models.CharField(max_length=50)
	balance = models.DecimalField(max_digits=8, decimal_places=2, blank=True)
	is_creditcard = models.BooleanField(default=False)
	
	def __str__(self):
		return "%s %s %s" %(self.name, self.balance, self.last_update)

class CreditCard(models.Model):
	account = models.ForeignKey(Account, on_delete=models.CASCADE)
	statement_balance = models.DecimalField(max_digits=8, decimal_places=2, blank=True)
	bill_date = models.DateField(blank=True)
	payment_scheduled_date = models.DateField(blank=True)
	payment_scheduled_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True)
	
	def __str__(self):
		return self.account.name
