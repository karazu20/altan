# Altan

Proyecto de Altan, ETLs y Miscelanea

## Prerrequisitos
- Python 2.7.13
- virtualenv
- python-pip

## Configuración
```
$ virtualenv .env
$ source .env/bin/activate
```

## Instalación
### Dependencias
```
$ pip install -r requirements.txt

```

## Ejecución ETL analitycs 'etl_analitycs'
Necesita parametros de ejecución periodo y tipo que por defaul debe ser 'analitycs', sólo debe de cambiar el periodo
Valores posibles de periodo ('all', 'month', 'week', 'day'), ejemplo:
```
$ python etl_analitycs.py "analitycs" "all"

```

## Ejecución ETL analitycs 'etl_custom_metric'
Necesita parametros de ejecución periodo y tipo que por defaul debe ser 'analitycs', sólo debe de cambiar el periodo
Valores posibles de periodo ('all', 'month', 'week', 'day'), ejemplo:
```
$ python etl_custom_metric.py "analitycs" "all"

```

 
