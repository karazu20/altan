# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
from requests.auth import HTTPBasicAuth
import json
import pandas as pd
from pandas.io.json import json_normalize
from influxdb import DataFrameClient
import time
import datetime
import numpy as np
from influxdb import InfluxDBClient
from time_utils import *
import sys


#load perios
print 'Argumentos: ' + str (sys.argv)
if len (sys.argv) < 3:
	print "Faltan argumentos"
	exit()
periodos  = get_periods (sys.argv[1], sys.argv[2])
periodo =sys.argv[2]
print periodos
init_date = periodos['start_date']
end_date =  periodos['end_date']


#credentials api management
user='abraham.martinez.ramirez@everis.com'
password='P4$$w0rd'
organizacion='altanredes'

#credentials flux DB
user_db = ''
password_db = ''
host='localhost'
port=8086
dbname = 'altan'

protocol = 'json'
serie_summary = 'apigee_analitycs_summary'
serie_custom = "apigee_metrics_custom"

#timestamp for normalize data
timestamp = unix_time_millis(datetime.datetime.strptime(init_date + ' 00:00:00','%m/%d/%Y %H:%M:%S'))


#Calculate availability and reliability
def calculate_facts(init_date,end_date, down_time, number_failures, requests, key):
	
	

	#Calculate availability	
	seconds_day = 24*60*60
	if periodo=='day':
		elapsed_time = seconds_day
	else:
		elapsed_time = (datetime.datetime.strptime(end_date, "%m/%d/%Y").date() - datetime.datetime.strptime(init_date, "%m/%d/%Y").date()).days * seconds_day
	

	availability = ((elapsed_time - down_time)/elapsed_time)*100	
	print key + ' availability --->'  + str(availability)


	#Calculate reliability	
	hours_efectives = (elapsed_time - down_time)/(60*60)	
	if number_failures!=0:
		reliability=hours_efectives/number_failures
	else:
		reliability = hours_efectives
	print key + ' reliability --->'  + str(reliability)
	timestamp_enddate = unix_time_millis(datetime.datetime.strptime(end_date + ' 00:00:00','%m/%d/%Y %H:%M:%S')) 

	#point to save in influxdb
	json_body = [
		{
			"measurement": serie_custom,
			"tags": {
				"Component": key				
			},
			"time": timestamp_enddate,
			"fields": {
				"availability": availability,
				"reliability": reliability,
				"errores_500":down_time,
				"fallos":number_failures,
				"requests":requests
				
			}
		}
	]

	return json_body




#urls of analitycs 
urls = {	
			'system_api_gee_500' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(response_status_code eq 500)&timeRange=" + init_date +"%2000:00~" + end_date+ "%2000:00&timeUnit=day",
			'system_api_gee_400' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(response_status_code eq 400)&timeRange=" + init_date +"%2000:00~" + end_date+ "%2000:00&timeUnit=day",
			'active_and_configuration_500' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(response_status_code eq 500 and apiproxy eq 'ActivationAndConfiguration')&timeRange=" + init_date + "%2000:00~" + end_date+ "%2000:00&timeUnit=day",
			'active_and_configuration_400' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(response_status_code eq 400 and apiproxy eq 'ActivationAndConfiguration')&timeRange=" + init_date + "%2000:00~" + end_date+ "%2000:00&timeUnit=day",
			'service_quality_manager_500' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(response_status_code eq 500 and apiproxy eq 'ServiceQualityManagement')&timeRange=" + init_date + "%2000:00~" + end_date + "%2000:00&timeUnit=day",
			'service_quality_manager_400' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(response_status_code eq 400 and apiproxy eq 'ServiceQualityManagement')&timeRange=" + init_date + "%2000:00~" + end_date + "%2000:00&timeUnit=day",
			'oauth_500' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(response_status_code eq 500 and apiproxy eq 'OAuthV2')&timeRange=" + init_date + "%2000:00~" + end_date + "%2000:00&timeUnit=day",
			'oauth_400' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(response_status_code eq 400 and apiproxy eq 'OAuthV2')&timeRange=" + init_date + "%2000:00~" + end_date + "%2000:00&timeUnit=day",
			'customer_management_500' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(response_status_code eq 500 and apiproxy eq 'CustomerManagement')&timeRange=" + init_date + "%2000:00~" + end_date + "%2000:00&timeUnit=day",
			'customer_management_400' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(response_status_code eq 400 and apiproxy eq 'CustomerManagement')&timeRange=" + init_date + "%2000:00~" + end_date + "%2000:00&timeUnit=day",
			'system_api_gee_errors' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&timeRange=" + init_date + "%2000:00~" + end_date + "%2000:00&timeUnit=day",			
			'active_and_configuration_errors' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(apiproxy eq 'ActivationAndConfiguration')&timeRange=" + init_date + "%2000:00~" + end_date + "%2000:00&timeUnit=day",
			'service_quality_manager_errors' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(apiproxy eq 'ServiceQualityManagement')&timeRange=" + init_date + "%2000:00~" + end_date + "%2000:00&timeUnit=day",
			'oauth_errors' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(apiproxy eq 'OAuthV2')&timeRange=" + init_date + "%2000:00~" + end_date + "%2000:00&timeUnit=day",
			'customer_management_errors' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(apiproxy eq 'CustomerManagement')&timeRange=" + init_date + "%2000:00~" + end_date + "%2000:00&timeUnit=day",
			'system_api_gee' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(message_count)&timeRange=" + init_date + "%2000:00~" + end_date + "%2000:00&timeUnit=day",			
			'active_and_configuration' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(message_count)&filter=(apiproxy eq 'ActivationAndConfiguration')&timeRange=" + init_date + "%2000:00~" + end_date + "%2000:00&timeUnit=day",
			'service_quality_manager' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(message_count)&filter=(apiproxy eq 'ServiceQualityManagement')&timeRange=" + init_date + "%2000:00~" + end_date + "%2000:00&timeUnit=day",
			'oauth' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(message_count)&filter=(apiproxy eq 'OAuthV2')&timeRange=" + init_date + "%2000:00~" + end_date + "%2000:00&timeUnit=day",
			'customer_management' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(message_count)&filter=(apiproxy eq 'CustomerManagement')&timeRange=" + init_date + "%2000:00~" + end_date + "%2000:00&timeUnit=day",


	}

panda_aux=None
panda=None

first=True


#Open client influx db
client = DataFrameClient(host, port, user_db, password_db, dbname)

#Send request to apigee analitycs and save time series into influx db
for key,value in urls.iteritems():
	print value
	myResponse = requests.get(value,auth=HTTPBasicAuth(user, password))
	
	# If response code is ok (200), get summary analitycs in dataframe
	if myResponse.status_code==200:


		# Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
	   	print '--------------------------------' + key + '-------------------------------'
		jData = json.loads(myResponse.content)
		panda = json_normalize(jData, ['environments','metrics','values'])
		
		if  panda.empty:
			d = {'timestamp': [timestamp] , 'value': [0.0]}
			panda = pd.DataFrame(data=d)
			

		panda = panda.set_index(['timestamp'])
		panda.index = pd.to_datetime(panda.index, unit='ms')
		panda.columns = [key]
		panda[key] = panda[key].astype(float).fillna(0.0)

		
		if not first:
			panda_aux = panda_aux.merge(panda, right_index=True, left_index=True,how='outer')
			panda_aux = panda_aux.astype(float).fillna(0.0)			
		
			
		else: 
			panda_aux=panda
			first=False				
		   
	else:
	  # If response code is not ok (200), print the resulting http error code with description
		myResponse.raise_for_status()


#Save Dataframe summary
#print panda_aux
client.write_points(panda_aux, serie_summary , protocol=protocol)
client.close()



#Save custom metrics  availability and reliability
client = InfluxDBClient(host, port, user, password, dbname)
keys = ['system_api_gee','active_and_configuration','service_quality_manager','oauth','customer_management']
for k in keys:
	try:
		down_time=panda_aux[k+'_500'].sum()
		number_failures = panda_aux[k + '_errors'].sum()
		requests = panda_aux[k].sum()
		metric = calculate_facts(init_date,end_date, down_time, number_failures, requests, k)
		client.write_points(metric)
	except KeyError:		
		print 'not exist key'
	
client.close()





