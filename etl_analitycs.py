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
end_date = "05/04/2018"

timestamp = unix_time_millis(datetime.datetime.strptime(init_date + ' 00:00:00','%m/%d/%Y %H:%M:%S')) * 1000000



"""
	{'access_token', 'api_product', 'apiproxy', 'apiproxy_revision', 'ax_cache_key', 'ax_cache_name', 'ax_cache_source', 'ax_day_of_week', 'ax_dn_region', 
   	'ax_execution_fault_flow_name', 'ax_execution_fault_flow_state', 'ax_execution_fault_policy_name', 'ax_geo_city', 'ax_geo_continent', 'ax_geo_country', 
    'ax_geo_region', 'ax_geo_timezone', 'ax_hour_of_day', 'ax_month_of_year', 'ax_true_client_ip', 'ax_ua_agent_family', 'ax_ua_agent_type','ax_ua_agent_version', 
    'ax_ua_device_category', 'ax_ua_os_family', 'ax_ua_os_version', 'ax_week_of_month', 'client_id', 'client_ip', 'developer', 'developer_app', 'developer_email', 
    'environment', 'flow_resource', 'gateway_flow_id', 'organization', 'proxy_basepath', 'proxy_client_ip',  'proxy_pathsuffix', 'request_path', 'request_uri', 
    'request_verb', 'response_status_code', 'target', 'target_basepath', 'target_host', 'target_ip', 'target_response_code', 'target_url', 'useragent', 'virtual_host', 'x_forwarded_for_ip'}   
"""
dimensions = {  'proxy':'apiproxy', 'target':'target', 'developer':'developer', 'api_product':'api_product'} 



"""
	{'sum(cache_hit)', 'sum(is_error)', 'sum(message_count)', 'sum(policy_error)', 'avg(request_processing_latency)', 'min(request_processing_latency)', 
	'max(request_processing_latency)', 'sum(request_size)', 'avg(request_size)', 'min(request_size)', 'max(request_size)', 'avg(response_processing_latency)', 
	'min(response_processing_latency)', 'max(response_processing_latency)', 'sum(response_size)', 'avg(response_size)', 'min(response_size)',  
	'max(response_size)', 'sum(target_error)', 'sum(target_response_time)', 'avg(target_response_time)', 'min(target_response_time)', 
	'max(target_response_time)', 'sum(total_response_time)', 'avg(total_response_time)', 'min(total_response_time)', 'max(total_response_time)'}
"""
metrics = { 'Errores ':'sum(is_error)', 'Requests':'sum(message_count)', }  #'sum(cache_hit)',



url_base =  'https://api.enterprise.apigee.com/v1/o/{0}/environments/prod/stats/{1}?select={2}&timeRange={3}%2000:00~{4}%2000:00&timeUnit=hour'
panda_aux=None
panda=None

bo=False
i=0
tags = {}
client = DataFrameClient(host, port, user_db, password_db, dbname)	

for key,value in dimensions.iteritems():
	dim = value
	tag = key
	for key,value in metrics.iteritems():
		
		metric = value
		value_column = key
		url = 'https://api.enterprise.apigee.com/v1/o/'+ organizacion+'/environments/prod/stats/'+ dim +'?select='+ metric +'&timeRange='+init_date+'%2000:00~'+end_date+'%2000:00&timeUnit=day' 		

		myResponse = requests.get(url,auth=HTTPBasicAuth(user, password))
																																																																																																																																																																																																																		
		if myResponse.status_code==200:
		   	#print '--------------------------------  ' + dim + '   ' + metric +'  -------------------------------'
			jData = json.loads(myResponse.content)

			for elem in jData['environments'][0]['dimensions'] :

				#print elem['name']
				#print json.dumps(elem, indent=4, sort_keys=True)
				panda = json_normalize(elem, ['metrics','values'])
				panda['elem']=elem['name']				
				panda.columns = ['time',value_column, tag]

				
				if  panda.empty:
					d = {'time': [timestamp] , value_column: [0.0], tag: ['-----']}
					panda = pd.DataFrame(data=d)
					#print panda	

				panda = panda.set_index(['time'])
				panda.index = pd.to_datetime(panda.index, unit='ms')
				
				panda[value_column] = panda[value_column].astype(float).fillna(0.0)
				panda[tag] = panda[tag].fillna('---------')

				#print panda
				   
		else:
		  # If response code is not ok (200), print the resulting http error code with description
			myResponse.raise_for_status()

ints(panda_aux, 'apigee_analitycs',tag_columns=dimensions.keys(), field_columns=metrics.keys())
client.close()

