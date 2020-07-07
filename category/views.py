from django.views.generic import ListView
from django.views.generic.base import TemplateView
from .models import Category
from budget.models import CategoryBudget
from transaction.models import Transaction
from decimal import Decimal
from django.db.models import Sum
from inthebank.views import view_date_control

class CategoryListView(ListView):
	model = Category
	template_name = 'category_list.html'

class SpendingByCategoryView(TemplateView):
	template_name='spendbycat.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		## For Title and Choosing Viewing Date			
		if self.kwargs:
			return_control=view_date_control(self.kwargs['year'],self.kwargs['month'])
		else:
			return_control=view_date_control(None, None)

		view_date = return_control['view_date']
		context['title']='Spending By Category '
		context['view_url']='spendbycat-list'
		context['prev']=return_control['prev']
		context['next']=return_control['next']
		context['view_date']=view_date
		## End of Title

		spendbycat_list=[]
		
		category_list=Category.objects.all().order_by('group__name','name')
		for category in category_list:
			category_sum=Transaction.objects.filter(
				category=category,
				date__month=view_date.month,
				date__year=view_date.year).aggregate(Sum('amount'))
			budget=CategoryBudget.objects.filter(category=category)
			category_item=[category,category_sum,budget]
			spendbycat_list.append(category_item)	

		context['spendbycat_list']=spendbycat_list

		return context










