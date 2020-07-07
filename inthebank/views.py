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
