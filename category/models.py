from django.db import models

BUDGET_METHOD = [
	('N','None'),
	('C','Constant Month to Month'),
	('A','Average over last 3 months'),
	('S','Scheduled Transactions'),
	('Y','Based on Last Year'),
	]
	
class CategoryGroup(models.Model):
	name = models.CharField(max_length=50)
	budget_method = models.CharField(max_length=1, choices=BUDGET_METHOD, default='N')

	def __str__(self):
		return '%s' %self.name

	class Meta:
		verbose_name='Category Group'
	

class Category(models.Model):
	name = models.CharField(max_length=50, blank=True)
	group = models.ForeignKey(CategoryGroup, on_delete=models.PROTECT)
	budget_method = models.CharField(max_length=1, choices=BUDGET_METHOD, default='N')

	def __str__(self):
		return '%s' %self.name
	
	class Meta:
		verbose_name_plural = 'Categories'
