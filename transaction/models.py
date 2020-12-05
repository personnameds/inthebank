from django.db import models
from category.models import Category

REPEAT_EVERY_CHOICES = [
	('M', 'Monthly'),
    ('B', 'Bi-Weekly'),
]	    

class Transaction(models.Model):
	date = models.DateField()
	description = models.CharField(max_length=100)
	amount = models.DecimalField(max_digits=8, decimal_places=2)
	category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
	
	def __str__(self):
		return '%s %s %s %s' %(self.date, self.description, self.amount, self.category)

#Saved Transactions change slightly each time
#Uses Amount, Partial Description and Category to find correct match
class SavedTransaction(models.Model):
	description = models.CharField(max_length=100)
	amount = models.DecimalField(max_digits=8, decimal_places=2)
	category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default=None)
	
	def __str__(self):
		return '%s %s %s' %(self.description, self.amount, self.category)

class ScheduledTransaction(models.Model):
	scheduled_date = models.DateField()
	description = models.CharField(max_length=100)
	amount = models.DecimalField(max_digits=8, decimal_places=2)
	category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)	
	repeat_every = models.CharField(max_length=2, choices=REPEAT_EVERY_CHOICES)
	
	def __str__(self):
		return '%s %s %s %s %s' %(self.scheduled_date, self.description, self.amount, self.category, self.repeat_every)