from django.db import models
from category.models import Category
	    
class Transaction(models.Model):
	date = models.DateField()
	description = models.CharField(max_length=250)
	amount = models.DecimalField(max_digits=8, decimal_places=2)
	category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
	
	def __str__(self):
		return '%s %s %s %s' %(self.date, self.description, self.amount, self.category)
        