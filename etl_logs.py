
import numpy as np
import pandas as pd
import pyodbc
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from pandas import DataFrame
import json
from time_utils import *
import sys
from message_utils import *
from tabulate import tabulate

#inout	transactionid	subtransactionid	target	resource	msisdn	apiparent	logtimestamp	operation	logdata	filename	responsecode	responsetype	iserror	processdate	processing_hour	be_id
INDEX_NAME = 'logs_bdl'

col = "inout,transactionid,subtransactionid,target,resource,msisdn,apiparent,logtimestamp,operation,logdata,filename,responsecode,responsetype,iserror,be_id" 
col_text="inout,transactionid,target,resource,apiparent,operation,logdata,filename,responsecode,responsetype" 
cols_notif="inout,transactionid,subtransactionid,target,msisdn,resource,operation,responsecode" 
#Deprecated
def as_pandas(cursor):
    names = col.split(",") 
    return pd.DataFrame([dict(zip(names, row)) for row in cursor], columns=names)

#Connection to impala
connection_string = '''DRIVER=/opt/cloudera/impalaodbc/lib/64/libclouderaimpalaodbc64.so;
HOST=34.237.230.77;
PORT=21051;
AuthMech=3;
UID=exteveris01;
PWD=rQGh4c'''

#load perios
print 'Argumentos: ' + str (sys.argv)
if len (sys.argv) < 3:
	print "Faltan argumentos"
	exit()
periodos  = get_periods (sys.argv[1], sys.argv[2])
print periodos
init_date = periodos['start_date']
end_date =  periodos['end_date']


#Querie get last transactions errors between period range 
querie = '''
		select %s from apigee.apigee_loganalysis where transactionid in 
		(SELECT  transactionid FROM  apigee.apigee_loganalysis where iserror=1 
			and  logtimestamp between '%s' and '%s' ) 
		order by transactionid, logtimestamp ;
		'''% (col, init_date,end_date)

print querie

#Connect to impala
connection = pyodbc.connect(connection_string, autocommit=True)
cursor = connection.cursor()


#Load pandas frame
df = pd.read_sql_query(querie, connection)


#Clean data '0x00'
fixer = dict.fromkeys([0x00], u'')

def repl(x):
	if x:
		return x.translate(fixer)
	else:
		return x

df.columns = col.split(",")
for c in col_text.split(","):
	df[c] = df[c].map(lambda x: repl(x) )



#Send alerts
errors = (df.loc[df['iserror'] == 1])[cols_notif.split(",")]

msg_email = tabulate(errors, headers='keys', tablefmt='orgtbl')
hours = periodos['start_date'] + ' - ' + periodos['end_date']
sendMail(msg_email, hours)

msg_slack = "# de Errores :"  + str (errors.shape[0]) + " en el periodo: " + hours  
print msg_slack
sendSlack (msg_slack)


# init ElasticSearch
es = Elasticsearch('http://localhost:9200/')

# Convert dataframe to json
df['logtimestamp'] = df['logtimestamp'].astype(str).apply(lambda x: x[:19])	
tmp = df.to_json(orient = "records")

# Load each record into json format before bulk
df_json= json.loads(tmp)
#print json.dumps(df_json, indent=4, sort_keys=True)

#save data into elsticsearch
bulk(es, df_json, index=INDEX_NAME, doc_type=INDEX_NAME )
print "Logs save success"
