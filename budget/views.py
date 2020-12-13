from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from category.models import Category, CategoryGroup
from transaction.models import Transaction, ScheduledTransaction
from django.db.models import Sum
from decimal import Decimal
from django.urls import reverse
from inthebank.views import view_title_context_data
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, WEEKLY
from datetime import datetime
from calendar import monthrange

class BudgetView(TemplateView):
	template_name = 'budget_list.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		view_title='Budget by Category for'	
		view_url='budget-list'
		
		context, view_date=view_title_context_data(self, context, view_url, view_title)

		now = datetime.now()
		last_day = datetime(now.year,now.month,monthrange(now.year, now.month)[1]).day

		budget_list=[]
		
		#All groups
		categorygroup_list=CategoryGroup.objects.all().order_by('name').exclude(name='Income')
		#For each group
		for categorygroup in categorygroup_list:
			categories = Category.objects.filter(group=categorygroup)
		
			group_sum = Transaction.objects.filter(
				category__in=categories,
				date__month=view_date.month,
				date__year=view_date.year).aggregate(Sum('amount'))
			
			category_list=[]
			for category in categories:
				cat_sum=Transaction.objects.filter(
					category=category,
					date__month=view_date.month,
					date__year=view_date.year).aggregate(Sum('amount'))
				
				st = ScheduledTransaction.objects.filter(category=category)
				if st:
					#Used get because I want it to fail if more than one category is being called
					#That will cause weird behaviours and I haven't accounted for it
					#Only works on bi-weekly payments
					st = ScheduledTransaction.objects.get(category=category)
					start_day = st.scheduled_date.day
					start_day=list(range(start_day, 1, -14))[-1]
					payments=len(list(range(start_day,last_day,14)))
					budget=payments * st.amount
				else:	
					budget=category.budget
				category_list.append((category,cat_sum,budget))
			
			budget_list.append((categorygroup,group_sum,category_list))
			
		context['budget_list']=budget_list
		return context

#For Updating/Editing Category Group Budgets
class CategoryGroupBudgetUpdateView(UpdateView):
	model=CategoryGroup
	template_name = 'update_budget_form.html'	
	fields=['budget',]

	def get_success_url(self, **kwargs):
		next=self.request.GET.get('next','/')
		return next

#For Updating/Editing Category Budgets
class CategoryBudgetUpdateView(UpdateView):
	model=Category
	template_name = 'update_budget_form.html'	
	fields=['budget',]

	def get_success_url(self, **kwargs):
		next=self.request.GET.get('next','/')
		return next