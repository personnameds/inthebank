from django.shortcuts import render
from django.views.generic.base import TemplateView
from category.models import Category, CategoryGroup
from django.db.models import Sum
from transaction.models import Transaction, ScheduledTransaction
from datetime import datetime
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, WEEKLY, MONTHLY
	
class ForecastTemplateView(TemplateView):
	template_name = 'forecast.html'	
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		#Hard Coded 6 months
		now = datetime.now()
		ld = now + relativedelta(months=5)
		last_day = datetime(ld.year, ld.month, monthrange(ld.month, ld.month)[1])
		first_month = datetime(now.year, now.month, 1)
		month_list= list(rrule(freq=MONTHLY, dtstart=first_month, interval=1, until=last_day))

#Group Category Spent CM M1 M2 M3 M4 M5

		#Income
		income_month=[]
		income_desc=[]
		income_total=[]
		
		categorygroup = CategoryGroup.objects.get(name='Income')
		categories = Category.objects.filter(group=categorygroup)
		
		for category in categories:
			st = ScheduledTransaction.objects.get(category=category)
			payment_list = rrule(freq=WEEKLY, dtstart=st.scheduled_date, interval=2, until=last_day)
			payments =[0]*len(month_list)
			
			#month_income=[]
			for m in month_list:
				payments=0
				for p in payment_list:
					if m.month == p.month:
						payments+=1
				income_month.append(payments*st.amount)

			income_desc.append(category.name)
		
		income_total.append(categorygroup.name)
		income_total.append([sum(income_month[i::len(month_list)]) for i in range(len(month_list))])
		
		income_month = [income_month[x:x+len(month_list)] for x in range(0,len(income_month),len(month_list))]

		income_list=zip(income_desc,income_month)

####DOESNT INCLUDE SCHEDULDED ITEMS
		#Budget
		budget_month=[]
		budget_desc=[]
		budget_total=[]
		
		exclude_list=['Income','Credit Cards']
		categorygroups = CategoryGroup.objects.all().exclude(name__in=exclude_list)
		
		for categorygroup in categorygroups:
			for m in month_list:
				group_spending = 0
				#Has a Category Group Budget
				if categorygroup.budget != 0:
					budget=categorygroup.budget
				else:
					budget=0
			
				#Categories in the Group
				categories = Category.objects.filter(group=categorygroup)
				for category in categories:
					#If Category has budget than Group does not
					#Add each category budget to get group budget
					if category.budget:
						budget += category.budget
				
					#Spending in Category Group
					#Get all Transactions in the Category
					transactions=Transaction.objects.filter(
													category=category,
													date__month=m.month,
													date__year=m.year)
					spending = transactions.aggregate(Sum('amount'))
					if spending['amount__sum'] is None:
						spending = 0
					else:
						spending = spending['amount__sum']
			
					group_spending += spending
###Need to think about what is minusing 
				if group_spending < budget:
					budget = 0
				else:
					budget = budget - group_spending
				
				budget_month.append(budget)
	
			budget_desc.append(categorygroup.name)
		
		budget_total.append('Total Budget')
		budget_total.append([sum(budget_month[i::len(month_list)]) for i in range(len(month_list))])
		budget_month = [budget_month[x:x+len(month_list)] for x in range(0,len(budget_month),len(month_list))]

		budget_list=zip(budget_desc,budget_month)



		
		net_month=[]
		net_month.append('Net')
		net_month.append([budget_total[1][i]+income_total[1][i] for i in range(len(month_list))])

		context['month_list'] = month_list
		
		context['income_list'] = income_list
		context['income_total'] = income_total
		
		context['budget_list'] = budget_list
		context['budget_total'] = budget_total	
		
		context['net_month'] = net_month
	
		return context
			
