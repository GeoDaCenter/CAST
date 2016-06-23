"""
"""

__author__  = "Xun Li <xunli@asu.edu> "
__all__ = ['FilterShapeList','Pydate2wxdate', 'Wxdate2pydate', 'GetIntervalStep','GetDateTimeIntervals']

import math, datetime
from datetime import timedelta

def FilterShapeList(shape_list, shape_type):
    """
    Filter shape file list by given shape-type
    """
    rtn_shape_list = []
    for shp in shape_list:
        if shp.shape_type == shape_type:
            rtn_shape_list.append(shp)
    return rtn_shape_list

def Pydate2wxdate(date): 
    """
    Module function: convert from Python Date
    to wx.Date type
    """
    tt = date.timetuple() 
    dmy = (tt[2], tt[1]-1, tt[0]) 
    return wx.DateTimeFromDMY(*dmy) 

def Wxdate2pydate(date): 
    """
    Module function: convert from wx.Date
    to Python Date type
    """
    if date.IsValid(): 
        ymd = map(int, date.FormatISODate().split('-')) 
        return datetime.date(*ymd) 
    else: 
        return None
    
def diff_month(d1, d2):
    total_months = (d2.year - d1.year) * 12
    total_months += d2.month - d1.month
    total_months += d2.day >= d1.day
    
    return total_months

def GetIntervalStep(query_date, start_date, step, step_by):
    """
    Given current_date, start_date, and step,
    return the index for current_date
    """
        
    if query_date < start_date:
        return -1
   
    step = float(step)
    
    if step_by == "Day" or step_by == "Week": 
        total_days = (query_date-start_date).days+1
        if step_by == "Day":
            current_steps = total_days/step
        elif step_by == "Week":
            current_steps = total_days/7.0/step
    else:
        total_months = diff_month(start_date,query_date)
        if step_by == "Month":
            current_steps = total_months/step
        elif step_by == "Year":
            current_steps = total_months/12.0/step
            
    steps = int(math.ceil(current_steps))
    return steps

def GetDateTimeIntervals(start, end, n, step, step_by):
    """
    return the [(start,end),(start,end),..] pairs 
    """
    import datetime
    from datetime import timedelta 
    interval_list = []
    interval_labels = []
    current = start
    
    if isinstance(start, datetime.date):
        for i in range(n):
            if   step_by == "Year":
                next_datetime = current.replace(year=current.year+1) 
                
            elif step_by == "Month":
                if current.month + step > 12:
                    next_datetime = current.replace(year=current.year+1)
                    next_datetime = next_datetime.replace(month=current.month+step-12)
                else:
                    next_datetime = current.replace(month=current.month+step)
    
            elif step_by == "Week":
                delta = timedelta(days=step*7)
                next_datetime =  current + delta 
                
            elif step_by == "Day":
                delta = timedelta(days=step)
                next_datetime =  current + delta 
            
            if i == n-1:
                next_datetime = end
                
            interval_labels.append(
                ('%2d/%2d/%4d'% (current.month,current.day,current.year),
                 '%2d/%2d/%4d'% (next_datetime.month,next_datetime.day,next_datetime.year))
            )
            interval_list.append((current, next_datetime))
            current = next_datetime
    else:
        # non-datetime format
        for i in range(n):
            next_one = start + i + 1
            interval_list.append((current,next_one))
            interval_labels.append(str(current))
            current += 1
    return interval_list, interval_labels
        
if __name__=="__main__":
    t1 = datetime.date(2012,1,1)
    t2 = datetime.date(2012,1,1)
    assert diff_month(t1,t2)==1
    assert GetIntervalStep(t2, t1, 1, "Month") == 0
    assert GetIntervalStep(t2, t1, 1, "Year") == 0
    
    t2 = datetime.date(2012,1,31)
    assert diff_month(t1,t2)==1
    assert GetIntervalStep(t2, t1, 1, "Month") == 0
    assert GetIntervalStep(t2, t1, 1, "Year") == 0
    
    t2 = datetime.date(2012,2,1)
    assert diff_month(t1,t2)==2
    assert GetIntervalStep(t2, t1, 1, "Month") == 1
    assert GetIntervalStep(t2, t1, 1, "Year") == 0

    t2 = datetime.date(2012,2,2)
    assert diff_month(t1,t2)==2
    assert GetIntervalStep(t2, t1, 1, "Month") == 1

    t2 = datetime.date(2012,2,28)
    assert diff_month(t1,t2)==2
    assert GetIntervalStep(t2, t1, 1, "Month") == 1
    
    t2 = datetime.date(2012,3,1)
    assert diff_month(t1,t2)==3
    assert GetIntervalStep(t2, t1, 1, "Month") == 2
    
    t2 = datetime.date(2012,12,31)
    assert diff_month(t1,t2)==12
    assert GetIntervalStep(t2, t1, 1, "Month") == 11
    
    t2 = datetime.date(2013,1,1)
    assert diff_month(t1,t2)==13
    assert GetIntervalStep(t2, t1, 1, "Month") == 12
    assert GetIntervalStep(t2, t1, 1, "Year") == 1

    t2 = datetime.date(2013,2,1)
    assert diff_month(t1,t2)==14
    assert GetIntervalStep(t2, t1, 1, "Month") == 13
    assert GetIntervalStep(t2, t1, 1, "Year") == 1
    
    
    t1 = datetime.datetime(2006, 9,1,0,0)
    t2 = datetime.datetime(2007, 7,27,0,0)
    assert GetIntervalStep(t2, t1, 1, "Month") == 10
    
    t2 = datetime.datetime(2007, 8,1,0,0)
    assert GetIntervalStep(t2, t1, 1, "Month") == 11
    
    t2 = datetime.datetime(2007, 8,20,0,0)
    assert GetIntervalStep(t2, t1, 1, "Month") == 11

    t1 = datetime.datetime(2006, 1,1,0,0)
    t2 = datetime.datetime(2009, 7,27,0,0)
    assert GetIntervalStep(t2, t1, 1, "Year") == 7
