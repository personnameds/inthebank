from django.db import models
from category.models import Category

REPEAT_EVERY_CHOICES = [
	('AM', 'Repeat Monthly on Approx. Specific Date'),
	('AB', 'Repeat Bi-Weekly on Approx. Specific Date'),
	('SM', 'Repeat Monthly on Specific Date'),
    ('B', 'Repeat Bi-Weekly based on Initial Date'),
]	    

class Transaction(models.Model):
	date = models.DateField()
	description = models.CharField(max_length=250)
	amount = models.DecimalField(max_digits=8, decimal_places=2)
	category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
	
	def __str__(self):
		return '%s %s %s %s' %(self.date, self.description, self.amount, self.category)

class ScheduledTransaction(models.Model):
	transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
	repeat_every = models.CharField(max_length=2, choices=REPEAT_EVERY_CHOICES, blank=True, null=True)
	working_date = models.DateField(blank=True, null=True)
	
	def __str__(self):
		return '%s is scheduled %s and for %s' %(self.transaction.description, self.repeat_every, self.working_date)