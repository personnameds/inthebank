from django.shortcuts import render
from django.views.generic.base import TemplateView
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, WEEKLY
from category.models import Category, CategoryGroup
from django.db.models import Sum
from transaction.models import Transaction, ScheduledTransaction
from datetime import datetime
from calendar import monthrange
	
	
class ForecastTemplateView(TemplateView):
	template_name = 'forecast.html'	
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

#Current Month
		now = datetime.now()
		last_day = datetime(now.year,now.month,monthrange(now.year, 1)[1])

		income_desc_list=[]
		income_num_list=[]
		
		categorygroup_list=CategoryGroup.objects.all().exclude(name='Income')

		#Income
		income_list = ScheduledTransaction.objects.filter(category__group__name='Income')
		for income_item in income_list:
			#Only need how many transactions per month
			income_dates=[]
			payments = (rrule(freq=WEEKLY, dtstart=income_item.scheduled_date, interval=2, until=last_day)).count()

			total = payments * income_item.amount
		
			income_desc_list.append(income_item.category.name)
			income_num_list.append(total)
			
		income_list=zip(income_desc_list,income_num_list)
		income_total=sum(income_num_list)

		budget_desc_list=[]
		budget_left_list=[]
		
		for categorygroup in categorygroup_list:
			
			group_spending=0
			#Has a Category Group budget
			if categorygroup.budget != 0:
				budget=categorygroup.budget
			else:
				budget=0

			categories=Category.objects.filter(group=categorygroup)
			for category in categories:
				#No Category Group budget so adding each category budget
				if category.budget:
					budget += category.budget

				#Spending in Category Group
				#Get all Categories in the Group
				#Get all Transactions in the Category				
				transactions=Transaction.objects.filter(
													category=category,
													date__month=now.month,
													date__year=now.year)
				spending=transactions.aggregate(Sum('amount'))
				if spending['amount__sum'] is None:
					spending=0
				else:
					spending=spending['amount__sum']
				group_spending += spending
			
			budget_left = budget - group_spending
	
			budget_desc_list.append(categorygroup.name)
			budget_left_list.append(budget_left)
			
			
		budget_list=zip(budget_desc_list,budget_left_list)
		month_forecast=income_total + sum(budget_left_list)

		context['now'] = now
		context['income_list'] = income_list
		context['income_total'] = income_total		
		context['budget_list'] =  budget_list
		context['month_forecast'] = month_forecast
		return context
			
