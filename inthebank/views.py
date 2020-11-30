import datetime
from dateutil.relativedelta import relativedelta #external library/extension python-dateutil

def view_date_control(year, month):

	today=datetime.date.today()

	if year:
		view_date=datetime.date(year,month,1)
		prev=view_date + relativedelta(months=-1)
		if view_date.month != today.month or view_date.year != today.year:
			next = view_date + relativedelta(months=+1)
		else:
			next = None
	else: #First load so starts with Today
		view_date=datetime.date.today()
		prev=view_date + relativedelta(months=-1)
		next = None		

	return {'prev':prev, 'next':next, 'view_date':view_date}

def view_title_context_data(self, context, view_url, view_title):
	## For Title and Choosing Viewing Date			
	if self.kwargs:
		return_control=view_date_control(self.kwargs['year'],self.kwargs['month'])
	else:
		return_control=view_date_control(None, None)

	view_date = return_control['view_date']
	context['title']=view_title
	context['view_url']=view_url
	context['prev']=return_control['prev']
	context['next']=return_control['next']
	context['view_date']=view_date
	## End of Title
	
	return context, view_date