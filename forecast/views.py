from django.views.generic.base import TemplateView
from budget.views import get_budget, get_spent, get_scheduledbudget, check_specific_budget
from budget.models import ScheduledBudget
from category.models import Category
from account.models import Account
from datetime import date
from dateutil.rrule import rrule, MONTHLY, WEEKLY
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from decimal import Decimal

class ForecastTemplateView(TemplateView):
	template_name = 'forecast.html'	
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		today = date.today()
		first_of_month = today.replace(day=1)
		month_list = list(rrule(freq=MONTHLY, count = 12, dtstart=first_of_month))
		
		account_list=[]
		accounts = Account.objects.all() #If accounts is empty this may fail

		income_categories = Category.objects.filter(group__name='Income')
		income_list=[]
		
		for income_category in income_categories:
			earned = get_spent(None, income_category, today)
			month_income_list, to_earn = get_scheduledbudget(None, income_category, earned, today, False, month_list)
			to_earn, month_income_list = check_specific_budget(to_earn, month_income_list, month_list, None, income_category)
			income_list.append((income_category, earned, to_earn , month_income_list))

		total_income_list = [sum(income_list[i][1] for i in range(len(income_list)))] #Total Current Earned
		total_income_list.append(sum(income_list[i][2] for i in range(len(income_list)))) #Total Current To Earn
		for m in range(len(month_income_list)):
			total_income_list.append(sum(income_list[i][3][m][1] for i in range(len(income_list))))
		
		budget_list= get_budget(today, month_list)
		total_budget_list = [sum(budget_list[i][0][1] for i in range(len(budget_list)))] # Total Current Spent

		#Total for Current Month To Spend
		to_spend = 0
		for i in range(len(budget_list)):
			#Group to Spend
			if budget_list[i][0][2]: #Check if Group to Spend
				to_spend += budget_list[i][0][2] #Group To Spend
			#Category to Spend
			else:
				if budget_list[i]: ##Why i??
					to_spend += (sum((budget_list[i][1][j][2] or 0) for j in range(len(budget_list[i][1])))) #Categories in Group
		total_budget_list.append(to_spend)

		#Rest of Months
		for m in range(len(month_list[1:])):
			total_month = 0
			for i in range(len(budget_list)):
				if budget_list[i][0][3]: #Checks if group budget
					total_month += budget_list[i][0][3][m][1]
				#Categories Rest of Month
				else:
					for j in range(len(budget_list[i][1])):
						if budget_list[i][1][j][3]:
							total_month += budget_list[i][1][j][3][m][1]
						
			total_budget_list.append(total_month)
			

		net_list = [total_income_list[i] + total_budget_list[i] for i in range(len(total_budget_list))]
		
		#Account Balance
		#Assumes Account[0] is Primary Bank Account
		#Current Month
		total_accounts = accounts.aggregate(Sum('balance'))
		total_accounts = total_accounts['balance__sum']
		current_month_balance = accounts[0].balance
		account_balance_list = [current_month_balance]
		
		#Rest of Momths
		month_balance = total_accounts #start with current_month - credit cards
		for m in range(len(month_list[1:])):
				month_balance = month_balance + net_list[m+1]
				account_balance_list.append(month_balance)

		context['accounts'] = accounts
		context['account_balance_list'] = account_balance_list
		context['month_list'] = month_list
		context['income_list'] = income_list
		context['total_income_list'] = total_income_list
		context['total_budget_list'] = total_budget_list
		context['budget_list'] = budget_list
		context['net_list'] = net_list

		return context
			
