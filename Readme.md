# Altan

Proyecto de Altan, ETLs y Miscelanea

## Prerrequisitos
- Python 2.7.13
- virtualenv
- python-pip
- libsasl2-2
- libsasl2-2-dev
- libsasl2-modules
- libsasl2-modules-db
- libsasl2-modules-gssapi-heimdal
- libsasl2-modules-gssapi-mit
- libsasl2-modules-ldap
- libsasl2-modules-otp
- libsasl2-modules-sql
- libkrb5-dev
- unixodbc-dev
- python-dev
- clouderaimpalaodbc_2.5.41.1029-2_amd64


## Configuración
```
$ virtualenv .env
$ source .env/bin/activate
```

## Instalación
### Dependencias Python
```
$ pip install -r requirements.txt

```

## Ejecución ETL analitycs 'etl_analitycs'
Necesita parametros de ejecución periodo y tipo que por defaul debe ser 'analitycs', sólo debe de cambiar el periodo
Valores posibles de periodo ('all', 'month', 'week', 'day'), ejemplo:
```
$ python etl_analitycs.py "analitycs" "all"

```

## Ejecución ETL analitycs metricas  disponibilidad y confiabilidad 'etl_custom_metric'
Necesita parametros de ejecución periodo y tipo que por defaul debe ser 'analitycs', sólo debe de cambiar el periodo
Valores posibles de periodo ('all', 'month', 'week', 'day'), ejemplo:
```
$ python etl_custom_metric.py "analitycs" "all"

```

## Ejecución ETL analitycs insumos csv para el bdl 'etl_bdl'
Necesita parametros de ejecución periodo y tipo que por defaul debe ser 'analitycs', sólo debe de cambiar el periodo
Valores posibles de periodo ('all', 'month', 'week', 'day'), ejemplo:
```
$ python etl_bdl.py "analitycs" "week"

```

## Ejecución ETL Logs  'etl_logs'
Necesita parametros de ejecución periodo y tipo que por defaul debe ser 'logs', sólo debe de cambiar el periodo
Valores posibles de periodo ('all', 'month', 'week', 'day', 'hour'), ejemplo:
```
$ python etl_logs.py "logs" "hour"

```

 
