from django.db import models

BUDGET_METHOD = [
	('N','None'),
	('C','Constant Month to Month'),
	('A','Average over last 3 months'),
	('S','Scheduled Transactions'),
	('Y','Based on Last Year'),
	]
	
def get_uncategorized_group():
	#Default Category Group is Uncategorized
	#Creates if it doesn't exist.
	group, created = CategoryGroup.objects.get_or_create(name='Uncategorized')
	return group.id

class CategoryGroup(models.Model):
	name = models.CharField(max_length=50)
	budget_method = models.CharField(max_length=1, choices=BUDGET_METHOD, default='N')

	def __str__(self):
		return '%s' %self.name

	class Meta:
		verbose_name='Category Group'
	
class Category(models.Model):
	name = models.CharField(max_length=50)
	group = models.ForeignKey(CategoryGroup, on_delete=models.SET_DEFAULT, default=get_uncategorized_group)
	budget_method = models.CharField(max_length=1, choices=BUDGET_METHOD, default='N')

	def __str__(self):
		return '%s' %self.name
	
	class Meta:
		verbose_name_plural = 'Categories'
