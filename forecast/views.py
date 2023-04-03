from django.views.generic.base import TemplateView
from category.models import Category, CategoryGroup
from transaction.models import Transaction
from envelope.models import Envelope
from budget.views import get_budget, get_scheduledbudget
from budget.models import ScheduledBudget, SpecifiedBudget
from datetime import date, datetime
from dateutil.rrule import rrule, MONTHLY, WEEKLY
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from calendar import monthrange
from account.models import Account

def get_schedule_forecast(group,category,from_date, to_date, month_list):
	if group:
		sb = ScheduledBudget.objects.get(categorygroup=group)
	else:
		sb = ScheduledBudget.objects.get(category=category)
	
	amount = sb.amount
	last_date = sb.last_date

	while from_date > last_date:
		last_date = last_date + relativedelta(weeks=2)
	from_date = last_date

	#2 weeks hardcoded in
	sched_months=[]
	sched_dates = list(rrule(freq=WEEKLY, interval=2, dtstart=from_date, until=to_date))
	for sd in sched_dates:
		sched_months.append(sd.month)

	forecast_list=[]
	for m in month_list:
		forecast_list.append(sched_months.count(m.month)*amount)

	return forecast_list

def get_year_forecast(group, category, month_list):
	forecast_list=[]		
	for m in month_list:
		from_date = m.replace(day=1)
		from_date = from_date + relativedelta(years=-1)
		to_date = from_date.replace(day=monthrange(from_date.year,from_date.month)[1])

		if group:
			categories = group.category_set.all()
			amount = Transaction.objects.filter(category__in=categories, date__gte=from_date, date__lte=to_date).aggregate(Sum('amount'))
		else:
			amount = Transaction.objects.filter(category=category, date__gte=from_date, date__lte=to_date).aggregate(Sum('amount'))
	
		amount = amount['amount__sum'] or 0
		forecast_list.append(amount)

	return forecast_list

class ForecastTemplateView(TemplateView):
	template_name = 'forecast.html'
    
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		today = date.today()

		#Hard Coded 12 Months
		from_date = today.replace(day=1)
		from_date = from_date + relativedelta(months=1)
		to_date = from_date + relativedelta(months=11, days=-1)
		month_list = list(rrule(freq=MONTHLY, dtstart=from_date, until=to_date))
		context['month_list'] = month_list

		transaction_list = Transaction.objects.filter(date__month=today.month, date__year=today.year)
		envelope_list = Envelope.objects.filter(date__month=today.month, date__year=today.year)
		specified_list = SpecifiedBudget.objects.filter(date__gte=from_date, date__lte=to_date)

		total=[]

##Acount Info
		account = Account.objects.get(name="TD All-Inclusive")
		total.append(account.balance)
		context['account'] = account

##Credit Card Info
		credit_cards = Account.objects.filter(is_creditcard=True)
		for credit_card in credit_cards:
			total[0] = total[0] + credit_card.balance
		context['credit_cards'] = credit_cards

##Start of Income
		income_category = Category.objects.get(name='TDSB')       
        
        #Income Earned - Current
		earned = transaction_list.filter(category=income_category).aggregate(Sum('amount'))
		earned = earned['amount__sum'] or 0
		
        #Income to Earn - Budget or Envelope - Current
		income_envelope = envelope_list.filter(category=income_category)
		
		if income_envelope:
			income_envelope = income_envelope[0].amount
		else:
			to_earn = get_scheduledbudget(None, income_category,today)

		#Simple subtraction because Scheduled
		to_earn = to_earn - earned
		total[0] = total[0] + to_earn
		#Income Forecast
		income_forecast = get_schedule_forecast(None, income_category, from_date, to_date, month_list)

		#Specified Budgets
		specified_budgets = specified_list.filter(category=income_category)
		for sp in specified_budgets:
			sp_date = datetime(sp.date.year, sp.date.month, 1, 0, 0)
			index = month_list.index(sp_date)
			income_forecast[index] = sp.amount

		for income in income_forecast:
			total.append(income)

		income_forecast = zip(income_forecast, month_list)
		
		income_list=(income_category, to_earn, income_forecast)

		context['income_list'] = income_list
## End of Income

##Credit Cards Need to be included

##Start of Categories
		group_list = CategoryGroup.objects.all().exclude(name='Credit Cards').exclude(name='Income')

		full_list=[]
		for group in group_list:

			#Category List
			categories = group.category_set.all()
			category_list=[]

			#Group Spent - Current
			group_spent = transaction_list.filter(category__in=categories).aggregate(Sum('amount'))
			group_spent = group_spent['amount__sum']
			
			#Group To Spend
			group_envelope = envelope_list.filter(categorygroup=group)
			if group_envelope:
				group_to_spend = group_envelope[0].amount
			else:
				group_to_spend = get_budget(group,None,group.budget_method,today)

			if group_spent:
				#For Scheduled budgets
				if group.budget_method == 'S':
					group_to_spend = get_scheduledbudget(group, None, today)
					group_to_spend = group_to_spend - -abs(group_spent)
				#Other budgets with Remainder
				elif group.remainder:
					group_to_spend = group_to_spend - -abs(group_spent)
				#Other Budget Types No Remainder
				else:
					group_to_spend = 0
			
			if group_to_spend:
				total[0] = total[0] + group_to_spend

			#Group Forecast
			if group.budget_method == 'S':
				group_forecast_list = get_schedule_forecast(group, None, from_date, to_date, month_list)
			elif group.budget_method == 'Y':
				group_forecast_list = get_year_forecast(group, None, month_list)
			else:
				amount = get_budget(group,None,group.budget_method,today)
				group_forecast_list=[]
				for m in month_list:
					group_forecast_list.append(amount)

			#Group Specified Budgets
			specified_budgets = specified_list.filter(categorygroup=group)
			for sp in specified_budgets:
				sp_date = datetime(sp.date.year, sp.date.month, 1, 0, 0)
				index = month_list.index(sp_date)
				group_forecast_list[index] = sp.amount

			for i in range(1,12):
				if group_forecast_list[i-1]:
					total[i] = total[i] + group_forecast_list[i-1]

			#Category Spent - Current
			for category in categories:
				category_spent = transaction_list.filter(category=category).aggregate(Sum('amount'))
				category_spent = category_spent['amount__sum']

				#Categroy To Spend
				category_envelope = envelope_list.filter(category=category)
				if category_envelope:
					category_to_spend = category_envelope[0].amount
				else:
					category_to_spend = get_budget(None,category,category.budget_method,today)

				if category_spent:		
					#For Scheduled budgets
					if category.budget_method == 'S':
						category_to_spend = get_scheduledbudget(None, category, today)
						category_to_spend = category_to_spend - -abs(category_spent)
					elif group.remainder:
						category_to_spend = None
					#Other Budget Types with Remainder
					elif category.remainder:
						category_to_spend = category_to_spend - -abs(category_spent)
					#Other Budget Types No Remainder
					else:
						category_to_spend = 0

				if category_to_spend:
					total[0] = total[0] + category_to_spend

				#Category Forecast
				if category.budget_method == 'S':
					category_forecast_list = get_schedule_forecast(None, category, from_date, to_date, month_list)
				elif category.budget_method == 'Y':
					category_forecast_list = get_year_forecast(None, category, month_list)
				else:
					amount = get_budget(None,category,category.budget_method,today)
					category_forecast_list=[]
					for m in month_list:
						category_forecast_list.append(amount)

				#Category Specified Budgets
				specified_budgets = specified_list.filter(category=category)
				for sp in specified_budgets:
					sp_date = datetime(sp.date.year, sp.date.month, 1, 0, 0)
					index = month_list.index(sp_date)
					category_forecast_list[index] = sp.amount

				for i in range(1,12):
					if category_forecast_list[i-1]:
						total[i] = total[i] + category_forecast_list[i-1]

				#Crategory List
				category_forecast_list = zip(category_forecast_list, month_list)
				category_list.append((category,category_to_spend,category_forecast_list))
	
			group_forecast_list = zip(group_forecast_list, month_list)

			full_list.append(((group,group_to_spend,group_forecast_list),category_list))
		
		balance = [0]*12
		balance[0] = total[0]
		for i in range(1,12):
			balance[i] = balance[i-1] + total[i]
		balance.pop(0)

		context['full_list'] = full_list
		context['total'] = total
		context['balance'] = balance
		return context