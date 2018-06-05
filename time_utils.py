from datetime import timedelta
import datetime
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime as dt


FORMAT_LOGS = '%Y-%m-%d %H:%M:%S' 
FORMAT_ANALITYCS = '%m/%d/%Y'


epoch = datetime.datetime.utcfromtimestamp(0)


def unix_time_millis(dt):
    return int((dt - epoch).total_seconds() * 1000)


def semana(date, format_date):

    # dow es Lunes = 1, Sabado = 6, Domingo = 7
    year, week, dow = date.isocalendar()
    # Si es el primer dia de la semana
    if dow == 1:
        # Calcular la fecha de la semana pasada
        start_date = date - timedelta(days=date.weekday()) + timedelta(weeks=-1)
    else:
        # Calcular el inicio de seman
        start_date = date - timedelta(days=date.weekday()) + timedelta(days=7, weeks=-2)
    # Agregar la fecha del fin de semana
    end_date = start_date + timedelta(6)
    
    #set hours
    start_date = start_date.replace(hour=00, minute=00,  second=00)
    end_date = end_date.replace(hour=23, minute=59,  second=59)

    print "Calculo por semana"
    start_date = str(start_date.strftime(format_date))
    end_date = str(end_date.strftime(format_date))

    result = {
        'start_date': start_date,
        'end_date': end_date
    }
    return result

def mes(date, format_date):

    # Obtener ultimo dia del mes anterior
    last_day = date + relativedelta(day=1, days=-1)

    # Agregar primer dia del mes
    first_day = last_day.replace(day=1)

    #set hours
    start_date = first_day.replace(hour=00, minute=00,  second=00)
    end_date = last_day.replace(hour=23, minute=59,  second=59)

    print "Calculo por mes"
    start_date = str(start_date.strftime(format_date))
    end_date = str(end_date.strftime(format_date))

    result = {
        'start_date': start_date,
        'end_date': end_date
    }

    return result    

def dia(date, format_date):

    last_day = date - timedelta(days=1)

    #set hours
    start_date = last_day.replace(hour=00, minute=00,  second=00)
    end_date = last_day.replace(hour=23, minute=59,  second=59)

    print "Calculo por dia"
    start_date = str(start_date.strftime(format_date))
    end_date = str(end_date.strftime(format_date))

    

    result = {
        'start_date': start_date,
        'end_date': end_date
    }
    
    return result    

def hora(date, format_date):

    last_hour = date - timedelta(hours=1)

    #set hours
    start_date = last_hour.replace(minute=00,  second=00)
    end_date = last_hour.replace(minute=59,  second=59)

    print "Calculo por hora anterior"
    start_date =  str (start_date.strftime(format_date))
    end_date =  str (end_date.strftime(format_date))

    result = {
        'start_date': start_date,
        'end_date': end_date
    }
    
    return result    


def todo(date,format_date ):
    
    init_date = dt.strptime("04/01/2018 00:00:00" ,'%m/%d/%Y %H:%M:%S')

    #set hours
    start_date = init_date.replace(hour=00, minute=00,  second=00)
    end_date = date.replace(hour=23, minute=59,  second=59)

    start_date = start_date.strftime(format_date)
    end_date = end_date.strftime(format_date)
    result = {
        'start_date': start_date,
        'end_date': end_date
    }
    return result


def get_periods (type_etl, option):
    if type_etl=='logs':
        format_date=FORMAT_LOGS
    elif type_etl=='analitycs':
        format_date=FORMAT_ANALITYCS
    else:
        print 'Format incorrect'
        exit()

    now = datetime.datetime.now()
    if option=="week":
        return semana(now,format_date)
    elif option=="day":
        return dia(now, format_date)
    elif option=="all":
        return todo(now, format_date)
    elif option=="hour":
        return hora(now, format_date)
    elif option=="month":
        return mes(now, format_date)
    else:
        print "Invalid periods"
        exit()


#semana(datetime.date(2018, 6, 4))

#mes(datetime.date(2018, 5, 1))

#dia(datetime.date(2018, 6, 1))

#hora(datetime.datetime.now())
