from django.shortcuts import render
from django.views.generic.base import TemplateView
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, WEEKLY, MONTHLY
from category.models import Category, CategoryGroup
from django.db.models import Sum
from transaction.models import ScheduledTransaction
from datetime import datetime
	
def get_months():
	#list of next 6 months
	num_months = 6
	now = datetime.now()
	last_day = now + relativedelta(months=num_months)
	month_list = [(now + relativedelta(months=i)) for i in range(num_months)]
	return last_day, month_list
	

class ForecastTemplateView(TemplateView):
	template_name = 'forecast.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		last_day, month_list = get_months()
		
		#Will contain all forecast items over the period
		#Need to add descriptions after so it can be summed using zip
		income_forecast_list=[]
		income_desc_list=[]
		
		#Income Only
		#Get Scheduled Income Items 
		#Only the next item is scheduled need to extrapolate the rest
		income_item_list = ScheduledTransaction.objects.filter(category__group__name='Income')
		for income_item in income_item_list:
			income_desc_list.append(income_item.description)
			#Only need how many transactions per month
			income_dates=[]
			for i in list(rrule(freq=WEEKLY, dtstart=income_item.scheduled_date, interval=2, until=last_day)):
				income_dates.append(i.month)
			
			income_forecast_item=[]
			for month in month_list:
				total = (income_dates.count(month.month)) * income_item.amount
				income_forecast_item.append(total)
			
			income_forecast_list.append(income_forecast_item)

		income_month_sum_list=list(map(sum,zip(*income_forecast_list)))

		#Add Category description back in
		for f in income_forecast_list:
			f.insert(0,income_desc_list.pop(0))
					
		#Scheduled Debit Items Only
		sched_debit_forecast_list=[]
		sched_desc_list=[]
		
		
		sched_debit_list = ScheduledTransaction.objects.exclude(category__group__name='Income')
		for sched_debit_item in sched_debit_list:
			sched_desc_list.append(sched_debit_item.description)
			
			sched_dates=[]
			if sched_debit_item.repeat_every == 'B':
				for i in list(rrule(freq=WEEKLY, dtstart=sched_debit_item.scheduled_date, interval=2, until=last_day)):
					sched_dates.append(i.month)	
			elif sched_debit_item.repeat_every == 'M':
				for i in list(rrule(freq=MONTHLY, dtstart=sched_debit_item.scheduled_date, interval=1, until=last_day)):
					sched_dates.append(i.month)	
			
			sched_forecast_item=[]
			for month in month_list:
				total = (sched_dates.count(month.month)) * sched_debit_item.amount
				sched_forecast_item.append(total)
			
			sched_debit_forecast_list.append(sched_forecast_item)
		
		sched_debit_month_sum_list=list(map(sum,zip(*sched_debit_forecast_list)))
				
		for f in sched_debit_forecast_list:
			f.insert(0,sched_desc_list.pop(0))


		context['month_list'] = month_list
		context['income_forecast_list'] = income_forecast_list
		context['income_month_sum_list'] = income_month_sum_list
		context['sched_debit_forecast_list'] = sched_debit_forecast_list
		context['sched_debit_month_sum_list'] = sched_debit_month_sum_list
		
		return context