# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
from requests.auth import HTTPBasicAuth
import json
import pandas as pd
from pandas.io.json import json_normalize
import time
import datetime
import numpy as np
from time_utils import *
import sys


#For calculate timestamp
epoch = datetime.datetime.utcfromtimestamp(0)
def unix_time_millis(dt):
	return int((dt - epoch).total_seconds() * 1000)

#Credentials api management
user='abraham.martinez.ramirez@everis.com'
password='P4$$w0rd'
organizacion='altanredes'


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
metrics_all = { 
				'Errores':'sum(is_error)', 'Requests':'sum(message_count)',
				'Promedio de respuesta (ms)':'avg(total_response_time)' , 
				'Minimo de respuesta (ms)':'min(total_response_time)', 'Maximo de respuesta (ms)':'max(total_response_time)' , 'Request size (bytes)':'avg(request_size)', 
				'Min request size (bytes)':'min(request_size)', 'Max request size (bytes)':'max(request_size)','Response size (bytes)':'sum(response_size)', 
				'Minimo response (bytes)':'min(response_size)','Maximo response (bytes)': 'max(response_size)'
			}  

metrics_base = { 'Errores':'sum(is_error)', 'Requests':'sum(message_count)'}  



analitycs = [
	
				# { 	
				# 	'name' : 'api_product',
				# 	'dimension' : 'api_product',
				# 	'metrics' : metrics_all
				# },

				# { 	
				# 	'name' : 'proxy',
				# 	'dimension' : 'proxy',
				# 	'metrics' : metrics_all
				# },

				# { 	
				# 	'name' : 'target',
				# 	'dimension' : 'target',
				# 	'metrics' : metrics_all
				# },

				# { 	
				# 	'name' : 'cliente',
				# 	'dimension' : 'client_id',
				# 	'metrics' : metrics_all
				# },

				# { 	
				# 	'name' : 'developer_app',
				# 	'dimension' : 'developer_app',
				# 	'metrics' : metrics_all
				# },

				# { 	
				# 	'name' : 'proxy_pathsuffix',
				# 	'dimension' : 'proxy_pathsuffix',
				# 	'metrics' : metrics_base
				# },

				{ 	
					'name' : 'request_path',
					'dimension' : 'request_path',
					'metrics' : metrics_base
				}				

		]




#for key,value in dimensions.iteritems():
for analityc in analitycs:	
	dim = analityc['dimension']
	tag = analityc['name']

	panda_aux=None
	panda=None

	bo=False
	i=0
	panda_tag = None
	pandas_list = {}

	for key,value in analityc['metrics'].iteritems():		
		metric = value
		value_column = key
		url = 'https://api.enterprise.apigee.com/v1/o/'+ organizacion+'/environments/prod/stats/'+ dim +'?select='+ metric +'&timeRange='+init_date+'%2000:00~'+end_date+'%2000:00&timeUnit=day' 		
		print url
		myResponse = requests.get(url,auth=HTTPBasicAuth(user, password))
		
		#If response is 200 then create frame from json																																																																																																																																																																																																																
		if myResponse.status_code==200:		   	
			jData = json.loads(myResponse.content)
			#print json.dumps(jData, indent=4, sort_keys=True)
			j = 0
			for elem in jData['environments'][0]['dimensions'] :
				print json.dumps(elem, indent=4, sort_keys=True)
				name = elem['name']
				print '--------------------------------' + key +  ' - ' + tag + ' - ' + name +  '-------------------------------'

				data_panda=None
				
				
				#Evaluate the index json with data
				if len (elem['metrics']) > 1:
					if len (elem['metrics'][0]['values']) > 1:						
						data_panda = elem['metrics'][0]['values']
					else :						
						data_panda = elem['metrics'][1]['values']
				else:						
					data_panda = elem['metrics'][0]['values']

				panda = json_normalize(data_panda)
				
				if  panda.empty:
					d = {'timestamp': [timestamp] , 'value': [0.0]}
					panda = pd.DataFrame(data=d)
					print panda
					
				#Create index time
				panda = panda.set_index(['timestamp'])
				panda.index = pd.to_datetime(panda.index, unit='ms')
				#panda.index.tz = None
				
				#Init frames and update frames 
				if name in pandas_list.keys():
					panda.columns = [ value_column]
					panda[value_column] = panda[value_column].astype(float).fillna(0.0)
					pandas_list[name] = pandas_list[name].merge(panda, right_index=True, left_index=True,how='outer')
				else:
					panda[tag] = name						
					panda.columns = [ value_column, tag]
					panda[value_column] = panda[value_column].astype(float).fillna(0.0)
					pandas_list[name]=panda
					
		
		else:
		  # If response code is not ok (200), print the resulting http error code with description
			myResponse.raise_for_status()
	
	# Order columns and clean rows with only 0 values
	for key, value in  pandas_list.iteritems():			
		columnsTitles = [tag] + analityc['metrics'].keys()	
		for c in columnsTitles:
			if c not in list(value.columns.values):
				value[c] = 0.0	
				print c					

		print list(value.columns.values)
		print key
		print columnsTitles
		pandas_list[key] = value[columnsTitles]				
	
	#Concat frames and save reults to csv and clean data	
	result = pd.concat(pandas_list.values())
	df = result[(result[analityc['metrics'].keys()] != 0).any(axis=1)]
	#result.to_csv(path_or_buf='csvs_bdl/panda_' + tag + '.csv')				   
	df.to_csv(path_or_buf='csvs_bdl/df_' + tag + '.csv')				   


