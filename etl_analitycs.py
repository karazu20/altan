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

serie = 'apigee_analitycs_generals'
protocol = 'json'

#load perios
print 'Argumentos: ' + str (sys.argv)
if len (sys.argv) < 3:
	print "Faltan argumentos"
	exit()
periodos  = get_periods (sys.argv[1], sys.argv[2])
print periodos
init_date = periodos['start_date']
end_date =  periodos['end_date']

#timestamp for normalize data
timestamp = unix_time_millis(datetime.datetime.strptime(init_date + ' 00:00:00','%m/%d/%Y %H:%M:%S')) 




"""  Dimensions
	{'access_token', 'api_product', 'apiproxy', 'apiproxy_revision', 'ax_cache_key', 'ax_cache_name', 'ax_cache_source', 'ax_day_of_week', 'ax_dn_region', 
   	'ax_execution_fault_flow_name', 'ax_execution_fault_flow_state', 'ax_execution_fault_policy_name', 'ax_geo_city', 'ax_geo_continent', 'ax_geo_country', 
    'ax_geo_region', 'ax_geo_timezone', 'ax_hour_of_day', 'ax_month_of_year', 'ax_true_client_ip', 'ax_ua_agent_family', 'ax_ua_agent_type','ax_ua_agent_version', 
    'ax_ua_device_category', 'ax_ua_os_family', 'ax_ua_os_version', 'ax_week_of_month', 'client_id', 'client_ip', 'developer', 'developer_app', 'developer_email', 
    'environment', 'flow_resource', 'gateway_flow_id', 'organization', 'proxy_basepath', 'proxy_client_ip',  'proxy_pathsuffix', 'request_path', 'request_uri', 
    'request_verb', 'response_status_code', 'target', 'target_basepath', 'target_host', 'target_ip', 'target_response_code', 'target_url'
    , 'useragent', 'virtual_host', 'x_forwarded_for_ip'}   
"""

"""	Metrics
	{'sum(cache_hit)', 'sum(is_error)', 'sum(message_count)', 'sum(policy_error)', 'avg(request_processing_latency)', 'min(request_processing_latency)', 
	'max(request_processing_latency)', 'sum(request_size)', 'avg(request_size)', 'min(request_size)', 'max(request_size)', 'avg(response_processing_latency)', 
	'min(response_processing_latency)', 'max(response_processing_latency)', 'sum(response_size)', 'avg(response_size)', 'min(response_size)',  
	'max(response_size)', 'sum(target_error)', 'sum(target_response_time)', 'avg(target_response_time)', 'min(target_response_time)', 
	'max(target_response_time)', 'sum(total_response_time)', 'avg(total_response_time)', 'min(total_response_time)', 'max(total_response_time)'}
"""

#Metrics to analize
metrics = { 'Errores':'sum(is_error)', 'Requests':'sum(message_count)' }  

#analitycs to consult 
analitycs = [
	
				{ 	
					'name' : 'api_product',
					'dimension' : 'api_product',
					'metrics' : metrics
				},

				{ 	
					'name' : 'proxy',
					'dimension' : 'apiproxy',
					'metrics' : metrics
				},

				{ 	
					'name' : 'target',
					'dimension' : 'target',
					'metrics' : metrics
				},

				{ 	
					'name' : 'cliente',
					'dimension' : 'client_id',
					'metrics' : metrics
				},

				{ 	
					'name' : 'developer_app',
					'dimension' : 'developer_app',
					'metrics' : metrics
				},

		]


panda=None

#init client influx db
client = DataFrameClient(host, port, user_db, password_db, dbname)	

#Send request to apigee analitycs and save time series into influx db
for analityc in analitycs:	
	dim = analityc['dimension']
	tag = analityc['name']
	for key,value in analityc['metrics'].iteritems():
		
		metric = value
		value_column = key
		url = 'https://api.enterprise.apigee.com/v1/o/'+ organizacion+'/environments/prod/stats/'+ dim +'?select='+ metric +'&timeRange='+init_date+'%2000:00~'+end_date+'%2000:00&timeUnit=day' 		
		print url
		myResponse = requests.get(url,auth=HTTPBasicAuth(user, password))
		# If response code is ok (200), save time series
		if myResponse.status_code==200:
		   	#print '--------------------------------  ' + dim + '   ' + metric +'  -------------------------------'
			jData = json.loads(myResponse.content)
			print json.dumps(jData, indent=4, sort_keys=True)
			for elem in jData['environments'][0]['dimensions'] :				
				#print json.dumps(elem, indent=4, sort_keys=True)
				panda = json_normalize(elem, ['metrics','values'])
				panda['elem']=elem['name']				
				panda.columns = ['time',value_column, tag]

				
				if  panda.empty:
					d = {'time': [timestamp] , value_column: [0.0], tag: ['-----']}
					panda = pd.DataFrame(data=d)
					print "panda vacio	"

				panda = panda.set_index(['time'])
				panda.index = pd.to_datetime(panda.index, unit='ms')
				
				panda[value_column] = panda[value_column].astype(float).fillna(0.0)
				panda[tag] = panda[tag].fillna('---------')
				#print panda
				client.write_points(panda, serie ,tag_columns=[tag], field_columns=[value_column], protocol=protocol)
				
				   
		else:
		  # If response code is not ok (200), print the resulting http error code with description
			myResponse.raise_for_status()

client.close()

