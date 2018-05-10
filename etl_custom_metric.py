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


epoch = datetime.datetime.utcfromtimestamp(0)
def unix_time_millis(dt):
	return int((dt - epoch).total_seconds() * 1000)


def calculate_facts(init_date,end_date, down_time, number_failures, key):
	
	 
	#Calculate availability
	print down_time	
	elapsed_time = (datetime.datetime.strptime(end_date, "%m/%d/%Y").date() - datetime.datetime.strptime(init_date, "%m/%d/%Y").date()).days*24*60*60
	availability = ((elapsed_time - down_time)/elapsed_time)*100	
	print key + ' availability --->' + str(availability)


	#Calculate reliability
	print number_failures
	hours_efectives = (elapsed_time - down_time)/(60*60)
	#print hours_efectives
	reliability=hours_efectives/number_failures
	print key + ' reliability --->'  + str(reliability)
	timestamp = unix_time_millis(datetime.datetime.strptime('04/26/2018 00:00:00','%m/%d/%Y %H:%M:%S')) * 1000000

	
	json_body = [
		{
			"measurement": "metrics_generals",
			"tags": {
				"Component": key				
			},
			"time": timestamp,
			"fields": {
				"availability": availability,
				"reliability": reliability,
				"errores_500":down_time,
				"fallos":number_failures
				
			}
		}
	]

	return json_body


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

init_date = "04/01/2018"
end_date = "04/25/2018"


#urls of analitycs
urls = {
			'system_api_gee_500' : 'https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(response_status_code eq 500)&timeRange=4/01/2018%2000:00~4/25/2018%2000:00&timeUnit=day',
			'active_and_configuration_500' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(response_status_code eq 500 and apiproxy eq 'ActivationAndConfiguration')&timeRange=4/01/2018%2000:00~4/25/2018%2000:00&timeUnit=day",
			'service_quality_manager_500' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(response_status_code eq 500 and apiproxy eq 'ServiceQualityManagement')&timeRange=4/01/2018%2000:00~4/25/2018%2000:00&timeUnit=day",
			'oauth_500' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(response_status_code eq 500 and apiproxy eq 'OAuthV2')&timeRange=4/01/2018%2000:00~4/25/2018%2000:00&timeUnit=day",
			'customer_management_500' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(response_status_code eq 500 and apiproxy eq 'CustomerManagement')&timeRange=4/01/2018%2000:00~4/25/2018%2000:00&timeUnit=day",
			'system_api_gee' : 'https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&timeRange=4/01/2018%2000:00~04/25/2018%2000:00&timeUnit=day',			
			'active_and_configuration' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(apiproxy eq 'ActivationAndConfiguration')&timeRange=4/01/2018%2000:00~4/25/2018%2000:00&timeUnit=day",
			'service_quality_manager' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(apiproxy eq 'ServiceQualityManagement')&timeRange=4/01/2018%2000:00~4/25/2018%2000:00&timeUnit=day",
			'oauth' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(apiproxy eq 'OAuthV2')&timeRange=4/01/2018%2000:00~4/25/2018%2000:00&timeUnit=day",
			'customer_management' : "https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&filter=(apiproxy eq 'CustomerManagement')&timeRange=4/01/2018%2000:00~4/25/2018%2000:00&timeUnit=day",

	}

respond=requests.get('https://api.enterprise.apigee.com/v1/o/altanredes/environments/prod/stats/?select=sum(is_error)&timeRange=4/01/2018%2000:00~4/25/2018%2000:00&timeUnit=month',auth=HTTPBasicAuth(user, password))
jData = json.loads(respond.content)
timestamp = np.int64 (jData['environments'][0]['metrics'][0]['values'][0]['timestamp'])

# For successful API call, response code will be 200 (OK)
panda_aux=None
panda=None

bo=False
i=0

client = DataFrameClient(host, port, user_db, password_db, dbname)


for key,value in urls.iteritems():

	myResponse = requests.get(value,auth=HTTPBasicAuth(user, password))
	
	
	if myResponse.status_code==200:


		# Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
	   	print '--------------------------------' + key + '-------------------------------'
		jData = json.loads(myResponse.content)
		panda = json_normalize(jData, ['environments','metrics','values'])
		
		if  panda.empty:
			d = {'timestamp': [timestamp] , 'value': [0.0]}
			panda = pd.DataFrame(data=d)
			#print panda	

		panda = panda.set_index(['timestamp'])
		panda.index = pd.to_datetime(panda.index, unit='ms')
		panda.columns = [key]
		panda[key] = panda[key].astype(float).fillna(0.0)

		#print panda		
		if bo:
			panda_aux = panda_aux.merge(panda, right_index=True, left_index=True,how='outer')
			panda_aux = panda_aux.astype(float).fillna(0.0)			
			#print panda_aux
			
		else: 
			panda_aux=panda
			bo=True						
		   
	else:
	  # If response code is not ok (200), print the resulting http error code with description
		myResponse.raise_for_status()

#print '--------------------------Super Panda--------------------------------'
#print panda_aux

#"Write DataFrame
client.write_points(panda_aux, 'errores_api_gee', protocol=protocol)
client.close()



client = InfluxDBClient(host, port, user, password, dbname)
keys = ['system_api_gee','active_and_configuration','service_quality_manager','oauth','customer_management']
for k in keys:
	try:
		down_time=panda_aux[k+'_500'].sum()
		number_failures = panda_aux[k].sum()
		metric = calculate_facts(init_date,end_date, down_time, number_failures, k)
		client.write_points(metric)
	except KeyError:		
		print 'not exist key'
	#print down_time
client.close()

#

#Create Frame form json





