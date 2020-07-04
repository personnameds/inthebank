from django.shortcuts import render
from django.views.generic.base import TemplateView
from budget.models import CategoryBudget
from transaction.models import Transaction
from django.db.models import Sum
import datetime
from dateutil.relativedelta import relativedelta #external library/extension python-dateutil

class BudgetByCategoryView(TemplateView):
	template_name = 'budgetbycategory.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
			
		today=datetime.date.today()

		if self.kwargs:
			year=self.kwargs['year']
			month = self.kwargs['month']
			view_date=datetime.date(year,month,1)
			prev=view_date + relativedelta(months=-1)
			if view_date.month != today.month or view_date.year != today.year:
				next = view_date + relativedelta(months=+1)
			else:
				next = None
		else: #Must be today
			view_date=datetime.date.today()
			prev=view_date + relativedelta(months=-1)
			next = None		

		context['prev']=prev
		context['next']=next
		context['view_date']=view_date

		budget_list=[]
		
		categorybudget_list=CategoryBudget.objects.all()
		for categorybudget in categorybudget_list:
			category=categorybudget.category
			category_sum=Transaction.objects.filter(
				category=category,
				date__month=view_date.month,
				date__year=view_date.year).aggregate(Sum('amount'))
			budget_item=[categorybudget.category,category_sum,categorybudget.amount]
			budget_list.append(budget_item)	

		context['budget_list']=budget_list

		return context

