from django.views.generic import ListView
from django.views.generic.base import TemplateView
from .models import Category, CategoryGroup
from transaction.models import Transaction
from decimal import Decimal
from django.db.models import Sum
from inthebank.views import view_date_control

class CategoryListView(ListView):
	model = Category
	template_name = 'category_list.html'

class SpendingView(TemplateView):
	template_name='spending_list.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		## For Title and Choosing Viewing Date			
		if self.kwargs:
			return_control=view_date_control(self.kwargs['year'],self.kwargs['month'])
		else:
			return_control=view_date_control(None, None)

		view_date = return_control['view_date']
		context['title']='Spending in'
		context['view_url']='spending-list'
		context['prev']=return_control['prev']
		context['next']=return_control['next']
		context['view_date']=view_date
		## End of Title

		##Group Category, Amount (sum of transactions), Budget
		##Table: Date, Description, Amount
		spending_list=[]
		
		
		#All Groups
		cat_group_list=CategoryGroup.objects.all().order_by('name')
		
		for cat_group in cat_group_list:

			#List of categories in the group
			cat_list=[]
			cat_list_in_group = Category.objects.filter(group=cat_group)
			group_sum = Transaction.objects.filter(
				category__in=cat_list_in_group,
				date__month=view_date.month,
				date__year=view_date.year).aggregate(Sum('amount'))
			
			#Each Category in the group
			for cat in cat_list_in_group:
				tran_list=Transaction.objects.filter(
					category=cat,
					date__month=view_date.month,
					date__year=view_date.year).order_by('date')
				cat_sum=tran_list.aggregate(Sum('amount'))
				
				cat_list.append((cat,cat_sum,tran_list))
				
			group_list=(cat_group,group_sum,cat_list)
			spending_list.append(group_list)	
		
		context['spending_list']=spending_list

		return context

# cat_group_list=CategoryGroup.objects.all().order_by('name')		
# #All the groups
# for cat_group in cat_group_list:
# 
# 	#List of categories in the group
# 	cat_list=[]
# 	cat_list_in_group = Category.objects.filter(group=cat_group)
# 	group_sum = Transaction.objects.filter(
# 		category__in=cat_list_in_group,
# 		date__month=view_date.month,
# 		date__year=view_date.year).aggregate(Sum('amount'))
# 	for cat_item in cat_list_in_group:
# 		cat_sum=Transaction.objects.filter(
# 			category=cat_item,
# 			date__month=view_date.month,
# 			date__year=view_date.year).aggregate(Sum('amount'))
# 		cat_list.append((cat_item,cat_sum))
# 	
# 	group_list=(cat_group,group_sum,cat_list)
# 	budget_list.append(group_list)
# 	
# context['budget_list']=budget_list
# return context





