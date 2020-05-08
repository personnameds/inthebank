from django.shortcuts import render
from django.views.generic.base import TemplateView
from transaction.models import Transaction, ScheduledTransaction
from category.models import Category
from budget.models import CategoryBudget
from django.db.models import Sum
import datetime

class BudgetByCategoryView(TemplateView):
	template_name = 'budgetbycategory.html'
	
	def get_context_data(self, **kwargs):
	
		today=datetime.date.today()
		
		context = super().get_context_data(**kwargs)
		categories = Category.objects.all()
		
		bycategory_list=[]
		for category in categories:
			transaction_sum=Transaction.objects.filter(date__month=today.month,date__year=today.year,category=category).aggregate(Sum('amount'))
			category_budget=CategoryBudget.objects.filter(category=category).first()
			scheduledtransaction=ScheduledTransaction.objects.filter(
												working_date__month=today.month,
												transaction__category=category,
												).aggregate(Sum('transaction__amount'))
			if category_budget:
				category_budget=category_budget.amount
			bycategory_list.append((category,transaction_sum,category_budget,scheduledtransaction))
		context['bycategory_list']=bycategory_list
		context['month']=today
		return context
