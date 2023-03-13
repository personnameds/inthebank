from django.db import models
from category.models import Category, CategoryGroup

REPEAT_EVERY_CHOICES = [
	('M', 'Monthly'),
    ('B', 'Bi-Weekly'),
]	    

def get_none_category():
	#Default category for Transaction is None in Uncategorized
	#Creates if it doesn't exist.
	group, created = CategoryGroup.objects.get_or_create(name='Uncategorized')
	category, created = Category.objects.get_or_create(
		name = 'None',
		group = group,
		)
	return category.id

class Transaction(models.Model):
	date = models.DateField()
	description = models.CharField(max_length=100)
	amount = models.DecimalField(max_digits=8, decimal_places=2)
	category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default=get_none_category)
	
	def __str__(self):
		return '%s %s %s %s' %(self.date, self.description, self.amount, self.category)
