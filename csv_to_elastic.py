
import pandas as pd 
import json

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


# init ElasticSearch
es = Elasticsearch('http://localhost:9200/')
INDEX_NAME = 'logs_bdl'

#load data json
df = pd.read_csv("query-impala-logs_0104_to_0506.csv", encoding="latin-1")

#trunc date to standard format
df['logtimestamp'] = df['logtimestamp'].astype(str).apply(lambda x: x[:19])
#df['processdate'] = df['processdate'].astype(str).apply(lambda x: x[:19])

#print df

# Convert into json
tmp = df.to_json(orient = "records")
# Load each record into json format before bulk
df_json= json.loads(tmp)
print json.dumps(df_json, indent=4, sort_keys=True)

#save data into elsticsearch
bulk(es, df_json, index=INDEX_NAME, doc_type=INDEX_NAME )