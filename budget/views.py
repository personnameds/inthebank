from category.models import Category, CategoryGroup
from .models import ConstantBudget, AvgQuarterBudget
from transaction.models import Transaction
from django.views.generic.base import TemplateView
from datetime import datetime
from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta
from django.db.models import Sum

class BudgetView(TemplateView):
	template_name='budget.html'


	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		show_all=self.request.GET.get('option')
		if show_all == 'showall':
			show_all=True
		else:
			show_all=False

		now = datetime.now()
		month_list = list(rrule(freq=MONTHLY, count = 12, dtstart=now))
		
		budget_list=[]
		
		categorygroups = CategoryGroup.objects.all().exclude(name='Income')
		
#Repetitive Code for CategoryGroup and Category
#Can make it more efficient
		
		for categorygroup in categorygroups:
			#If Budget by Category Group
			if categorygroup.budget_method != 'N' or show_all:

				#Group Spending	
				categories = categorygroup.category_set.all()

				spent = Transaction.objects.filter(category__in=categories, date__month=now.month, date__year=now.year).aggregate(Sum('amount'))
				if spent['amount__sum'] == None:
					spent = 0
				else:
					spent = spent['amount__sum']

				if categorygroup.budget_method != 'N':				
					#Group Budget
					if categorygroup.budget_method == 'C':
						group_budget_object=ConstantBudget.objects.get(categorygroup=categorygroup)	
						month_budget_list=[group_budget_object.amount]*11

						if group_budget_object.remainder:				
							budget_left = min(0,group_budget_object.amount - spent)
						elif spent:
							budget_left = 0
						else:
							budget_left = month_budget or 0
				
					#Add to Budget List	
					budget_list.append((categorygroup.name,None,spent,budget_left,month_budget_list))

			
			#If Budget by Category
			if categorygroup.budget_method == 'N' or show_all:
				
				categories = Category.objects.filter(group=categorygroup)
				category_list = []
				
				for category in categories:

					spent = Transaction.objects.filter(category=category, date__month=now.month, date__year=now.year).aggregate(Sum('amount'))
					if spent['amount__sum'] == None:
						spent = 0
					else:
						spent = spent['amount__sum']
					
					#Category spending
					if category.budget_method != 'N':
						
						#Category Budget
						if category.budget_method == 'C':
							budget_object = ConstantBudget.objects.get(category=category)
							month_budget = budget_object.amount
							month_budget_list = [budget_object.amount]*11
						
						elif category.budget_method == 'A':
							budget_object =  AvgQuarterBudget.objects.get(category=category)
							
							from_date = now.replace(day=1)
							to_date = now.replace(day=1)							
							from_date = from_date + relativedelta(months=-3)
							to_date = to_date + relativedelta(days=-1)
							
							month_budget=Transaction.objects.filter(category=category, date__gte=from_date, date__lte=to_date).aggregate(Sum('amount'))
							month_budget=month_budget['amount__sum']/3
							
							month_budget_list = [month_budget]*11

						if budget_object.remainder:
							budget_left = min(0,month_budget - spent)
						elif spent:
							budget_left = 0
						else:
							budget_left = month_budget
					else:
						budget_left = None
						month_budget_list = None	
					
					#Add to Category List
					category_list.append((category.name,spent,budget_left,month_budget_list))
				
				#Add to Budget List
				budget_list.append((categorygroup.name,category_list))
		
		context['month_list'] = month_list
		context['budget_list'] = budget_list
		context['title'] = 'Budget for Year'
		context['show_all'] = show_all
		return context

